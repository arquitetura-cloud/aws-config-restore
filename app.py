#!/usr/bin/env python3
import sys

from app.loadconfigs import MenuOptions
from app.normalizeparameters import NormalizeParameters
from typing import List
import boto3
import botocore.exceptions
from deepdiff import DeepDiff
import json
from simple_term_menu import TerminalMenu
from pygments import formatters, highlight, lexers
import os
import jmespath
from pprint import pprint

# local list storing all history about changes
_hidden_config_list = []

#main error handler

def error_handler(CliError):
    print(f'Error! \n {CliError} \n Are your access or credentias valid ?')
    input("Press Enter to Continue")
    menu()

# get all available AWS regions
def get_regions(service_name: str) -> List[str]:
    region_list = []
    if len(boto3.session.Session().get_available_regions(service_name)) == 0:
        region_list.append("Global Resource")
    else:
        region_list = boto3.session.Session().get_available_regions(service_name)
    return region_list
# list all cloudfront distributions
def list_distributions(region):
    client = boto3.client('cloudfront')
    try:
        response = client.list_distributions()
        distributions = []
        for item in response['DistributionList']['Items']:
            # list that will be used by the menu
            distributions.append("Id:{} - DomainName: {} - Alias({}): {} ".format(item['Id'], item['DomainName'], str(item['Aliases']['Quantity']), item['Aliases']['Items'][0] if item['Aliases']['Quantity'] > 0 else "No Alias"))
        return distributions
    except botocore.exceptions.ClientError as CliError:
         error_handler(CliError)

# get config history for a given resource ID in a region
def get_configuration_history(resource_id, region_name='us-east-1'):
    configurationChanges: list[str] = []

    try:
        client = boto3.client('config', region_name=region_name)
        response = client.get_resource_config_history(
            resourceType='AWS::CloudFront::Distribution',
            resourceId=resource_id,
            limit=10
        )
        for item in response['configurationItems']:
            # local list storing all history about changes
            _hidden_config_list.append(item)
            # list that will be used by the menu
            configurationChanges.append("ChangeID: {} - Date: {} - Status: {}".format(item['configurationStateId'],
                                                                                      item['configurationItemCaptureTime'],
                                                                                      item['configurationItemStatus']))
        return configurationChanges
    except botocore.exceptions.ClientError as CliError:
        error_handler(CliError)

# preview a configuration change
def preview_configuration(selectedConfiguration):
    configurationChangeId = selectedConfiguration.split(" - ")[0].replace("ChangeID: ", "")
    # retrieve the configuration from _hidden_config_list by mathing with its configurationStateId
    for item in _hidden_config_list:
        # print("DEBUG: {} == {} -> {} #####".format(item['configurationStateId'], configurationChangeId, item['configurationStateId'] == configurationChangeId))
        if item['configurationStateId'] == configurationChangeId:
            configurationJson = json.loads(item['configuration'])
            lexer = lexers.get_lexer_by_name("json", stripnl=False, stripall=False)
            formatter = formatters.TerminalFormatter(bg="dark")  # dark or light
            highlighted_file_content = highlight(json.dumps(configurationJson, indent=4), lexer, formatter)
            return highlighted_file_content


# compare two configurations
def compare_configurations(newConfig, oldConfig):
    # here I compare FROM config2(older) to config1(newer)
    result = DeepDiff(json.loads(oldConfig), json.loads(newConfig), ignore_order=True)
    # iterate and print all differences
    print(result)


def menu():
    # Main menu asking for user to select a supported AWS Service:
    main_menu_items = MenuOptions().__call__()
    main_menu_title = "Select a supported AWS Service"
    main_menu_cursor = "> "
    main_menu_cursor_style = ("fg_red", "bold")
    main_menu_style = ("bg_red", "fg_yellow")
    main_menu_exit = False

    main_terminal_menu = TerminalMenu(
        title=main_menu_title,
        show_search_hint=True,
        menu_entries=main_menu_items,
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style,
        cycle_cursor=True,
        clear_screen=True,
                                      )
    while not main_menu_exit:
        menu_entry_index = main_terminal_menu.show()
        if menu_entry_index == len(main_menu_items) or main_menu_items[menu_entry_index] == "Quit":
            main_menu_exit = True
            sys.exit(0)
        else:
            region_menu_title = f" {main_menu_items[menu_entry_index]}.\n Select Region. \n"
            region_menu_items = get_regions(MenuOptions().get_service_name(main_menu_items[menu_entry_index]))
            region_menu_items.append("Back to previous Menu")
            region_menu_back = False
            region_menu = TerminalMenu(
                region_menu_items,
                title=region_menu_title,
                menu_cursor=main_menu_cursor,
                menu_cursor_style=main_menu_cursor_style,
                menu_highlight_style=main_menu_style,
                cycle_cursor=True,
                clear_screen=True,
                show_search_hint=True,
            )

            while not region_menu_back:
                region_menu_entry_index = region_menu.show()
                if region_menu_entry_index == len(region_menu_items) or region_menu_entry_index == None or region_menu_items[region_menu_entry_index] == "Back to previous Menu":
                    region_menu_back = True
                    main_menu_exit = False
                    break
                else:
                    service_menu_title = f" {main_menu_items[menu_entry_index]} > {region_menu_items[region_menu_entry_index]}.\n Select Resource. "
                    service_menu_items = list_distributions({region_menu_items[region_menu_entry_index]})
                    service_menu_items.append("Back to previous Menu")
                    service_menu_back = False
                    service_menu = TerminalMenu(
                        service_menu_items,
                        title=service_menu_title,
                        menu_cursor=main_menu_cursor,
                        menu_cursor_style=main_menu_cursor_style,
                        menu_highlight_style=main_menu_style,
                        cycle_cursor=True,
                        clear_screen=True,
                    )
                    while not service_menu_back:
                        service_menu_entry_index = service_menu.show()
                        if service_menu_entry_index == len(service_menu_items) or service_menu_entry_index == None or service_menu_items[service_menu_entry_index] == "Back to previous Menu":
                            service_menu_back = True
                            region_menu_back = False
                            main_menu_exit = False
                            break
                        else:
                            #print('Do nasty stuff')
                            distributionId = service_menu_items[service_menu_entry_index].split(" - ")[0].split(":")[1]
                            configurationList = get_configuration_history(distributionId)
                            configuration_menu_title = f" {main_menu_items[menu_entry_index]} > {region_menu_items[region_menu_entry_index]} > {distributionId}.\n Select Configuration: "
                            configuration_menu_items = configurationList
                            configuration_menu_items.append("Back to previous Menu")
                            configuration_menu_back = False
                            configuration_menu = TerminalMenu(
                                configuration_menu_items,
                                title=configuration_menu_title,
                                menu_cursor=main_menu_cursor,
                                menu_cursor_style=main_menu_cursor_style,
                                menu_highlight_style=main_menu_style,
                                cycle_cursor=True,
                                clear_screen=True,
                                show_search_hint=False,
                                preview_command=preview_configuration,
                                preview_size=0.75,
                            )

                            while not configuration_menu_back:
                                configuration_menu_entry_index = configuration_menu.show()
                                if configuration_menu_entry_index == len(configuration_menu_items) or configuration_menu_entry_index == None or configuration_menu_items[configuration_menu_entry_index] == "Back to previous Menu":
                                    configuration_menu_back = True
                                    service_menu_back = False
                                    break
                                else:
                                    configurationChangeId = configuration_menu_items[configuration_menu_entry_index].split(" - ")[0].replace("ChangeID: ", "")
                                    yesno_menu_title = f" {main_menu_items[menu_entry_index]} > {region_menu_items[region_menu_entry_index]} > {distributionId} > {configurationChangeId}.\n Apply Configuration? "
                                    yesno_menu_items = ['Yes', 'No', 'Back to previous Menu']
                                    yesno_menu_back = False
                                    yesno_menu = TerminalMenu(
                                        yesno_menu_items,
                                        title=yesno_menu_title,
                                        menu_cursor=main_menu_cursor,
                                        menu_cursor_style=main_menu_cursor_style,
                                        menu_highlight_style=main_menu_style,
                                        cycle_cursor=True,
                                        clear_screen=True,
                                        show_search_hint=False,
                                    )

                                    while not yesno_menu_back:
                                        yesno_menu_entry_index = yesno_menu.show()
                                        if yesno_menu_entry_index == len(yesno_menu_items) or yesno_menu_entry_index == None or yesno_menu_items[yesno_menu_entry_index] == "Back to previous Menu":
                                            yesno_menu_back = True
                                            break
                                        elif yesno_menu_items[yesno_menu_entry_index] == 'Yes':
                                            apply_configuration(distributionId, configurationChangeId)
                                            print('Configuration Applied!')
                                            input("Press Enter to continue...")
                                            yesno_menu_back = True
                                            service_menu_back = True
                                            region_menu_back = True
                                            break

                                        elif yesno_menu_items[yesno_menu_entry_index] == 'No':
                                            yesno_menu_back = True
                                            break
                                        else:
                                            break


def apply_configuration(distributionId, configurationChangeId):
    """Applies a configuration to a distribution

    Args:
        distributionId (_type_): Cloudfront distribution ID
        configurationChangeId (_type_): Configuration Change ID from AWS Config
    """
    # retrieve the configuration from _hidden_config_list by mathing with its configurationStateId
    config = json.loads(__search_configuration_local(configurationChangeId))
    if config is not None:
        converted_config = __convert_history_item_into_next_config(config)
        print(f'------\n {converted_config}')
        normalize_converted_config = NormalizeParameters(converted_config).normalize()
        print(f'------\n {normalize_converted_config}')
        try:
            # apply the configuration to the distribution
            client = boto3.client('cloudfront')
            response = client.update_distribution(
                Id=distributionId,
                DistributionConfig=normalize_converted_config,
                IfMatch=__get_distribution_etag(distributionId)
            )
            print("Configuration applied to distribution {}".format(distributionId))
            input("Press Enter to continue...")
            menu()
        except botocore.exceptions.ClientError as CliError:
            error_handler(CliError)

# get current cloudfront distribution configuration etag
def __get_distribution_etag(distributionId):
    client = boto3.client('cloudfront')
    response = client.get_distribution(
        Id=distributionId
    )
    return response['ETag']


# helper method to find a configuration at local cache
def __search_configuration_local(configurationChangeId):
    for item in _hidden_config_list:
        if item['configurationStateId'] == configurationChangeId:
            return item['configuration']


# helper method to capitalize json key names
def __capitalize_json_elements(x):
    if isinstance(x, list):
        return [__capitalize_json_elements(v) for v in x]
    elif isinstance(x, dict):
        return {k[0].upper() + k[1:]: __capitalize_json_elements(v) for k, v in x.items()}
    else:
        return x


# helper method to convert a past config into a deployable config
def __convert_history_item_into_next_config(config):
    new_config = json.loads(json.dumps(config['distributionConfig']))
    #new_config = __capitalize_json_elements(new_config)
    #new_config['ViewerCertificate']['SSLSupportMethod'] = new_config['ViewerCertificate'].pop(
    #    'SslSupportMethod')  # manually changed, due to expected API format

    return new_config


# def highlight_change(configurationChangeId):

# with open(filepath, "r") as f:
#     file_content = f.read()
# try:
#     lexer = lexers.get_lexer_for_filename(filepath, stripnl=False, stripall=False)
# except ClassNotFound:
#     lexer = lexers.get_lexer_by_name("text", stripnl=False, stripall=False)
# formatter = formatters.TerminalFormatter(bg="dark")  # dark or light
# highlighted_file_content = highlight(file_content, lexer, formatter)
# return highlighted_file_content


# main function
def main():
    # displays the initial menu
    menu()


# main handler
if __name__ == "__main__":
    main()
