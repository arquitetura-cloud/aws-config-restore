## Install as script
 - Clone this repo
 - `pip install -r requirements.txt`
 - `cd aws_config_restore`
 - `cd app`
    ### Run
    ` python -m app`
## Install as pip package

- pip install aws-config-restore
- ` aws-config-restore`


## Config References:
https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html

## About

AWS Config Restore tool restore previous configuration recorded in AWS Config Service.
This tool converts AWS Config records into parameters for boto3 API calls. Initially only AWS Cloudfront will be supported, but new services will be added

Features:

- Interactive menu to show options 
- Confirmation before apply configuration
- Uses boto3 parameter reference to compare AWS Config data with AWS Config records.