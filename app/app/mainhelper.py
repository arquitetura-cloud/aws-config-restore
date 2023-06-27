import boto3
import botocore
from typing import List
import json
from pygments import formatters, highlight, lexers
from deepdiff import DeepDiff
from app.app import wafhelper
from app.app import cloudfronthelper
from app.app import normalizeparameters

wafhelper = wafhelper.waftools()
cloudfronthelper = cloudfronthelper.cloudfronttools()
normalizeparameters = normalizeparameters.NormalizeParameters()


def error_handler(CliError):
    print(f'Error! \n {CliError} \n Are your access or credentias valid ?')
    input("Press Enter to Continue")


class MainHelper:

    def __init__(self):
        self._hidden_config_list: list[dict] = []
        self.configurationChanges: list[str] = []
        self.config = boto3.client('config', region_name='us-east-1')

    def get_regions(self, service_name: str) -> List[str]:
        region_list = []
        if len(boto3.session.Session().get_available_regions(service_name)) == 0:
            # region_list.append("Global Resource")
            pass
        else:
            region_list = boto3.session.Session().get_available_regions(service_name)
        return region_list

    def get_configuration_history(self, resource_id, resourcetype, region_name='us-east-1'):
        self.configurationChanges = []
        try:
            response = self.config.get_resource_config_history(
                resourceType=str(resourcetype),
                # 'AWS::CloudFront::Distribution',resourcetype,  # 'AWS::CloudFront::Distribution',
                resourceId=str(resource_id),
                limit=10
            )

            for item in response['configurationItems']:
                # local list storing all history about changes
                self._hidden_config_list.append(item)
                # list that will be used by the menu
                self.configurationChanges.append(
                    "ChangeID: {} - Date: {} - Status: {} - ResourceType: {}".format(item['configurationStateId'],
                                                                                     item[
                                                                                         'configurationItemCaptureTime'],
                                                                                     item[
                                                                                         'configurationItemStatus'],
                                                                                     item['resourceType']
                                                                                     )
                )
            return self.configurationChanges  # , self._hidden_config_list
        except botocore.exceptions.ClientError as CliError:
            error_handler(CliError)

    def preview_configuration(self, selectedConfiguration):
        configurationChangeId = selectedConfiguration.split(" - ")[0].replace("ChangeID: ", "")
        # retrieve the configuration from _hidden_config_list by mathing with its configurationStateId
        for item in self._hidden_config_list:
            # print("DEBUG: {} == {} -> {} #####".format(item['configurationStateId'], configurationChangeId, item['configurationStateId'] == configurationChangeId))
            if item['configurationStateId'] == configurationChangeId:
                configurationJson = json.loads(item['configuration'])
                lexer = lexers.get_lexer_by_name("json", stripnl=False, stripall=False)
                formatter = formatters.TerminalFormatter(bg="dark")  # dark or light
                highlighted_file_content = highlight(json.dumps(configurationJson, indent=4), lexer, formatter)
                return highlighted_file_content

    def compare_configurations(self, newConfig, oldConfig):
        # here I compare FROM config2(older) to config1(newer)
        result = DeepDiff(json.loads(oldConfig), json.loads(newConfig), ignore_order=True)
        # iterate and print all differences
        print(result)

    def get_resource_id_by_name(self, resource_name, resourcetype):
        resourceid = ""
        try:
            response = self.config.list_discovered_resources(
                resourceType=resourcetype,
            )
            if len(response['resourceIdentifiers']) > 0:
                for item in response['resourceIdentifiers']:
                    if item.get('resourceName') is not None:
                        if item['resourceName'] == resource_name:
                            resourceid = item['resourceId']
                            break
                    else:
                        if item['resourceId'] == resource_name:
                            resourceid = item['resourceId']
                            break

            else:
                pass
        except botocore.exceptions.ClientError as e:
            print(e)
            return False

        return resourceid

    def get_resource_id_from_config(self, resourcetypes):
        resources = []

        for resourcetype in resourcetypes:
            try:
                response = self.config.list_discovered_resources(
                    resourceType=resourcetype,
                )
                if len(response['resourceIdentifiers']) > 0:
                    for item in response['resourceIdentifiers']:
                        resources.append(
                            "ResourceType : {} - ResourceName : {}".format(item['resourceType'],
                                                                           item['resourceName'] if item.get(
                                                                               'resourceName') is not None else
                                                                           item.get('resourceId')
                                                                           )
                        )
                else:
                    continue
            except botocore.exceptions.ClientError as e:
                print(e)
                return False

        return resources

    # compare two configurations
    def get_distribution_etag(distributionId):  # Todo, move to cloudfront helper.
        client = boto3.client('cloudfront')
        response = client.get_distribution(
            Id=distributionId
        )
        return response['ETag']

    # helper method to find a configuration at local cache
    def search_configuration_local(self, configurationChangeId):
        for item in self._hidden_config_list:
            if item['configurationStateId'] == configurationChangeId:
                return item['configuration']

    # helper method to convert a past config into a deployable config
    def convert_history_item_into_next_config(self, config):
        new_config = json.loads(json.dumps(config['distributionConfig']))
        # new_config = __capitalize_json_elements(new_config)
        # new_config['ViewerCertificate']['SSLSupportMethod'] = new_config['ViewerCertificate'].pop(
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

    def apply_configuration(self, resourcename, configurationChangeId, resourcetype):
        """Applies a configuration to a resource

        Args:
            resourcename (_type_): Cloudfront distribution ID
            configurationChangeId (_type_): Configuration Change ID from AWS Config
            resourcetype (_type_): Resource type ( From AWS Config)
        """
        # retrieve the configuration from _hidden_config_list cache by mathing with its configurationStateId
        config = json.loads(self.search_configuration_local(configurationChangeId))

        if config is not None:

            # If the resource type is Cloudfront Distriburion, first Normalize the
            # the Case in parameter strings. Then pass to respective function
            if resourcetype == 'AWS::CloudFront::Distribution':
                normalize_converted_config = normalizeparameters.normalize(config['distributionConfig'])
            else:
                normalize_converted_config = config

            try:
                # apply the configuration to the resource
                # call the correct function based on the resource type
                if resourcetype == 'AWS::CloudFront::Distribution':
                    cloudfronthelper.apply_cloudfront_configurations(
                        resourcename,
                        normalize_converted_config
                    )

                elif resourcetype == 'AWS::WAFv2::WebACL':

                    wafhelper.apply_waf_configurations(
                        resourceid=self.get_resource_id_by_name(resourcename, resourcetype),
                        resourcetype=resourcetype,
                        resource_configuration=normalize_converted_config,
                        resourcename=resourcename
                    )
                elif resourcetype == 'AWS::WAFv2::RuleGroup':
                    pass
                elif resourcetype == 'AWS::WAFv2::IPSet':
                    pass
                elif resourcetype == 'AWS::WAFv2::RegexPatternSet':
                    pass
                elif resourcetype == 'AWS::WAFv2::ManagedRuleSet':
                    pass
                print("Configuration applied to resource {}".format(resourcename))

                return True


            except botocore.exceptions.ClientError as CliError:
                error_handler(CliError)

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
    """
