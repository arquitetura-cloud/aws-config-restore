#!/usr/bin/env python3
import sys
from app.app.loadconfigs import MenuOptions,  LoadConfigs
from app.app import mainhelper
from app.app import wafhelper
from app.app import cloudfronthelper
from simple_term_menu import TerminalMenu


#main helper
mainhelper = mainhelper.MainHelper()
#waf helper
wafhelper = wafhelper.waftools()
#cloudfront helper
cloudfronthelper = cloudfronthelper.cloudfronttools()

#main error handler

def error_handler(CliError):
    print(f'Error! \n {CliError} \n Are your access or credentias valid ?')
    input("Press Enter to Continue")

    menu()
def menu():
    # Main menu asking for user to select a supported AWS Service:
    main_menu_items = MenuOptions().__call__()
    main_menu_title = "Select a supported AWS Service"
    main_menu_cursor = "> "
    main_menu_cursor_style = ("fg_red", "bold")
    main_menu_style = ("bg_red", "fg_yellow")
    main_menu_exit = False
    # Main menu
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
            # Service Selected. Region Menu
            region_menu_title = f" {main_menu_items[menu_entry_index]}.\n Select Region. \n"
            region_menu_items = mainhelper.get_regions(LoadConfigs.get_service_name(LoadConfigs(), resource_name=main_menu_items[menu_entry_index]))
            # Append Back option to the region menu.
            region_menu_items.append("Back to previous Menu")
            # Append Global(Cloudfront) to the top of menu
            region_menu_items.insert(0, "Global(CloudFront)")
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
                    #Region Selected. Resource Menu
                    service_menu_title = f" {main_menu_items[menu_entry_index]} > {region_menu_items[region_menu_entry_index]}.\n Select Resource. "
                    # Based on the selected service, choose the resource.
                    # The resource come from get_resource_id_from_config in
                    # the MainHelper Class.
                    # Lists all resources discovered by config using the ResourceTypes
                    # parameters in config.yaml file.
                    # How it works:
                    # Load all menu data. From there, compare the options with
                    # the selected option. If Match, call MainHelper.get_resource_id_from_config to
                    # return a list of resource IDs and names.
                    # WAF is a group of resources, so when I select WAF, a condition
                    # loop in all references to get the resources related to WAF check config.yaml file for details
                    service_menu_items = []

                    # if main_menu_items[menu_entry_index] == "AWS Cloudfront":
                    #     service_menu_items = cloudfronthelper.list_distributions({region_menu_items[region_menu_entry_index]})
                    # elif main_menu_items[menu_entry_index] == "AWS WAF":

                    for option, data in MenuOptions().menu_data['menu_options'].items():
                        # print(option)
                        if data['DisplayName'] == main_menu_items[menu_entry_index]:
                            service_menu_items = mainhelper.get_resource_id_from_config(data['ResourceTypes'])
                    # Add back to previous menu option
                    service_menu_items.append("Back to previous Menu")
                    service_menu_back = False
                    # Show the Resources Menu
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



                            # configurationList = []
                            # if main_menu_items[menu_entry_index] == "AWS Cloudfront":
                            #
                            #     distributionId = service_menu_items[service_menu_entry_index].split(" - ")[0].split(":")[1]
                            #     configurationList = get_configuration_history(distributionId)
                            # else:



                            resourcename = service_menu_items[service_menu_entry_index].split(" : ")[-1]
                            resourcetype = service_menu_items[service_menu_entry_index].split(" : ")[1].split(' - ')[0]
                            resourceid = mainhelper.get_resource_id_by_name(resourcename, resourcetype)
                            configurationList = mainhelper.get_configuration_history(resourceid, resourcetype)
                            configuration_menu_title = f" {main_menu_items[menu_entry_index]} > {region_menu_items[region_menu_entry_index]} > {resourcename}.\n Select Configuration: "
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
                                preview_command=mainhelper.preview_configuration,
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
                                    yesno_menu_title = f" {main_menu_items[menu_entry_index]} > {region_menu_items[region_menu_entry_index]} > {resourcename} > {configurationChangeId}.\n Apply Configuration? "
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
                                            if mainhelper.apply_configuration(resourcename, configurationChangeId, resourcetype):

                                                print('Configuration applied Successfully!')
                                                input("Press Enter to continue...")
                                                yesno_menu_back = True
                                                service_menu_back = True
                                                region_menu_back = True
                                                break
                                            else:
                                                print('Configuration failed to apply!')
                                                input("Press Enter to continue...")

                                        elif yesno_menu_items[yesno_menu_entry_index] == 'No':
                                            yesno_menu_back = True
                                            break
                                        else:
                                            break

# main function
def main():
    # displays the initial menu
    menu()


# main handler
if __name__ == "__main__":
    main()
