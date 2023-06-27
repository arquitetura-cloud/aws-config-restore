import botocore
import boto3
from app.app import mainhelper

def error_handler(CliError):
    print(f'Error! \n {CliError} \n Are your access or credentias valid ?')
    input("Press Enter to Continue")

class cloudfronttools:
    def __init__(self):
        self.cloudfront = boto3.client('cloudfront', region_name='us-east-1')

    def apply_cloudfront_configurations(self, resourceid,resource_configuration):

        try:
            response = self.cloudfront.update_distribution(
                Id=resourceid,
                DistributionConfig=resource_configuration,
                IfMatch=mainhelper.MainHelper.get_distribution_etag(resourceid)
            )
        except botocore.exceptions.ClientError as CliError:
            error_handler(CliError)
    def list_distributions(self, region):
        try:
            response = self.cloudfront.list_distributions()
            distributions = []
            for item in response['DistributionList']['Items']:
                # list that will be used by the menu
                distributions.append("Id:{} - DomainName: {} - Alias({}): {} ".format(item['Id'], item['DomainName'],
                                                                                      str(item['Aliases']['Quantity']),
                                                                                      item['Aliases']['Items'][0] if
                                                                                      item['Aliases'][
                                                                                          'Quantity'] > 0 else "No Alias"))
            return distributions
        except botocore.exceptions.ClientError as CliError:
            error_handler(CliError)
