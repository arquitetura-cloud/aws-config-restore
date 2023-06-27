import botocore
import boto3

class waftools:
    def __init__(self):
        self.wafv2 = boto3.client('wafv2', region_name='us-east-1')

    def apply_waf_configurations(self, resourcetype, resourceid, resourcename, resource_configuration, scope='CLOUDFRONT'):
        # :param resourcetype: Type of the resource to be configured.
        # :param resourceid: Id of  the resource to be configured.
        # :param configuration: Resource configuration to be applied,  in json format.
        # :return: Sucess or  failure message.

        # Based on the resource type,  the  appropriate wafv2  method  is  called.

        if resourcetype == 'AWS::WAFv2::WebACL':
            # Script Required parameters to API:
            # Default Action
            # Description
            # Id
            # Name
            # Scope
            # VisibilityConfig
            # Rules
            # LockToken

            # get the real id from the arn from AWS Config.
            #Simply split the last / from string:
            real_resource_id = resourceid.split('/')[-1]

            # First, get the lock token for the Web ACL:

            getwebacl = self.wafv2.get_web_acl(
                Id=real_resource_id,
                Name=resourcename,
                Scope=scope
            )
            locktoken = getwebacl['LockToken']

            # Construct the values dictionary for the updatewebacl API
            # using resource_configuration  as  the  source:
            values = {
                "Id": real_resource_id,
                "Name": resourcename,
                "Scope": scope}
            if resource_configuration.get('DefaultAction') is not None:
                values['DefaultAction'] = resource_configuration['DefaultAction']
            if resource_configuration.get('Description') is not None:
                values['Description'] = resource_configuration['Description']
            if resource_configuration.get('VisibilityConfig') is not None:
                values['VisibilityConfig'] = resource_configuration['VisibilityConfig']
            if resource_configuration.get('Rules') is not None:
                values['Rules'] = resource_configuration['Rules']
            values['LockToken'] = locktoken
            if resource_configuration.get('AssociationConfig') is not None:
                values['AssociationConfig'] = resource_configuration['AssociationConfig']
            if resource_configuration.get('CaptchaConfig') is not None:
                values['CaptchaConfig'] = resource_configuration['CaptchaConfig']
            if resource_configuration.get('CustomResponseBodies') is not None:
                values['CustomResponseBodies'] = resource_configuration['CustomResponseBodies']
            if resource_configuration.get('TokenDomains') is not None:
                values['TokenDomains'] = resource_configuration['TokenDomains']

            #return values

            # Now,  update  the  WebACL  with  the  new     configuration:
            try:
                updatewebacl = self.wafv2.update_web_acl(**values)
                return(f'Configuration applied successfully: \n {updatewebacl}')
            except botocore.exceptions.ClientError as e:
                return(e.response['Error']['Message'])

        elif resourcetype == 'AWS::WAFv2::RuleGroup':

            pass

        elif resourcetype == 'AWS::WAFv2::IPSet':
            pass

        elif resourcetype == 'AWS::WAFv2::RegexPatternSet':
            pass

        elif resourcetype == 'AWS::WAFv2::ManagedRuleSet':
            pass
