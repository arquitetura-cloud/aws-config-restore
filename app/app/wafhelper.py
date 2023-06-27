import botocore
import boto3

class waftools:
    def __init__(self):
        self.wafv2 = boto3.client('wafv2', region_name='us-east-1')

    def apply_waf_configurations(self, resourcetype, resourceid, resourcename, resource_configuration, scope='CLOUDFRONT'):
        # :param resourcetype: Type of the resource to be configured.
        # :param resourceid: Id of  the resource to be configured.
        # :param configuration: Resource configuration to be applied,  in json format.
        # :return: Success or  failure message.

        # Based on the resourcetype parameter,  the  appropriate wafv2  method  is  called.

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
            # Simply split the last / from string:
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
                if len(resource_configuration['Description']) > 0:
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
                return f'Configuration applied successfully: \n {updatewebacl}'
            except botocore.exceptions.ClientError as e:
                return e.response['Error']['Message']

        elif resourcetype == 'AWS::WAFv2::RuleGroup':

            # Script Required parameters to API:
            # Name
            # Scope
            # Id
            # Description
            # Rules
            # VisibilityConfig
            # LockToken
            # CustomResponseBodies

            # get the real id from the arn from AWS Config.
            # Simply split the last / from string:
            real_resource_id = resourceid.split('/')[-1]

            # First, get the lock token for the Rule Group. This ensure that the
            # configuration is not overwritten:

            getrulegroup = self.wafv2.get_rule_group(
                Id=real_resource_id,
                Name=resourcename,
                Scope=scope
            )
            locktoken = getrulegroup['LockToken']

            # Construct the values dictionary for the update_rule_group API
            # using resource_configuration  as  the  source:
            # Obs.: Not all configs need to be present. So, to prevent
            # Keys errors in dictionary,  we  check  for  each  config  and
            # Validate if it is not None. If it is None,  we  skip  it.

            values = {
                "Name": resourcename,
                "Scope": scope,
                "Id": real_resource_id
                }
            if resource_configuration.get('Description') is not None:
                if len(resource_configuration['Description']) > 0:
                    values['Description'] = resource_configuration['Description']

            if resource_configuration.get('Rules') is not None:
                values['Rules'] = resource_configuration['Rules']

            if resource_configuration.get('VisibilityConfig') is not None:
                values['VisibilityConfig'] = resource_configuration['VisibilityConfig']

            values['LockToken'] = locktoken

            if resource_configuration.get('CustomResponseBodies') is not None:
                values['CustomResponseBodies'] = resource_configuration['CustomResponseBodies']

            # return values
            # Now,  update  the  WebACL  with  the  new     configuration:
            try:
                updaterulegroup = self.wafv2.update_rule_group(**values)
                return f'Configuration applied successfully: \n {updaterulegroup}'
            except botocore.exceptions.ClientError as e:
                return e.response['Error']['Message']

        elif resourcetype == 'AWS::WAFv2::IPSet':

            # Script Required parameters to API:
            # Name
            # Scope
            # Id
            # Description
            # Addresses
            # LockToken

            # get the real id from the arn from AWS Config.
            # Simply split the last / from string:
            real_resource_id = resourceid.split('/')[-1]

            # First, get the lock token for the Rule Group. This ensure that the
            # configuration is not overwritten:

            getipset = self.wafv2.get_ip_set(
                Id=real_resource_id,
                Name=resourcename,
                Scope=scope
            )
            locktoken = getipset['LockToken']

            # Construct the values dictionary for the update_rule_group API
            # using resource_configuration  as  the  source:
            # Obs.: Not all configs need to be present. So, to prevent
            # Keys errors in dictionary,  we  check  for  each  config  and
            # Validate if it is not None. If it is None,  we  skip  it.

            values = {
                "Name": resourcename,
                "Scope": scope,
                "Id": real_resource_id
                }
            if resource_configuration.get('description') is not None:
                if len(resource_configuration['description']) > 0:
                    values['Description'] = resource_configuration['description']

            if resource_configuration.get('addresses') is not None:
                values['Addresses'] = resource_configuration['addresses']

            values['LockToken'] = locktoken

            # return values
            # Now,  update  the  WebACL  with  the  new     configuration:
            try:
                updateipset = self.wafv2.update_ip_set(**values)
                return f'Configuration applied successfully: \n {updateipset}'
            except botocore.exceptions.ClientError as e:
                return e.response['Error']['Message']

        elif resourcetype == 'AWS::WAFv2::RegexPatternSet':
            # Script Required parameters to API:
            # Name
            # Scope
            # Id
            # Description
            # Rules
            # VisibilityConfig
            # LockToken
            # CustomResponseBodies

            # get the real id from the arn from AWS Config.
            # Simply split the last / from string:
            real_resource_id = resourceid.split('/')[-1]

            # First, get the lock token for the Rule Group. This ensure that the
            # configuration is not overwritten:

            getregexpatternset = self.wafv2.get_regex_pattern_set(
                Id=real_resource_id,
                Name=resourcename,
                Scope=scope
            )
            locktoken = getregexpatternset['LockToken']

            # Construct the values dictionary for the update_rule_group API
            # using resource_configuration  as  the  source:
            # Obs.: Not all configs need to be present. So, to prevent
            # Keys errors in dictionary,  we  check  for  each  config  and
            # Validate if it is not None. If it is None,  we  skip  it.

            values = {
                "Name": resourcename,
                "Scope": scope,
                "Id": real_resource_id
            }
            if resource_configuration.get('Description') is not None:
                if len(resource_configuration['Description']) > 0:
                    values['Description'] = resource_configuration['Description']

            if resource_configuration.get('regularExpressionList') is not None:
                values['RegularExpressionList'] = resource_configuration['regularExpressionList']

            values['LockToken'] = locktoken

            # return values
            # Now,  update  the  WebACL  with  the  new     configuration:
            try:
                updateregexpatternset = self.wafv2.update_regex_pattern_set(**values)
                return f'Configuration applied successfully: \n {updateregexpatternset}'
            except botocore.exceptions.ClientError as e:
                return e.response['Error']['Message']

        elif resourcetype == 'AWS::WAFv2::ManagedRuleSet':
            pass
