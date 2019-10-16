
import boto3
import datetime

def lambda_handler(event, context):
    ec = boto3.client('ec2')
    account_ids = ['YOUR AWS ACCOUNT NUMBER']
    filters = [
        {'Name': 'tag-key', 'Values': ['Type']},
        {'Name': 'tag-value', 'Values': ['Backup']},
    ]
    snapshots = ec.describe_snapshots(OwnerIds=account_ids, Filters=filters)

    output = {}
    count = 0
    for snap in snapshots['Snapshots']:
        line = ''

        # make dict out of tags
        tags = {}
        for tag in snap['Tags']:
            tags[tag["Key"]] = tag["Value"]
        
        # compute days remaining
        expiration_date = datetime.datetime.strptime(tags['Expiration Date'], '%Y-%m-%d %H:%M:%S')
        past_expiration_days = (expiration_date - datetime.datetime.now()).days
        
        # determine whether to delete
        expiration_offset = 0 # default 0
        if past_expiration_days < expiration_offset:
            # delete snapshot
            line += 'Delete {snapshot} ({days} days old)'.format(snapshot = snap['SnapshotId'], days = past_expiration_days)
            ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
             
            # handle output
            output[count] = line
            count += 1

            # avoid boto RequestLimitExceeded
            # only delete 4 at a time
            if count > 25:
                break;
                

    if count == 0:
        return 'No snapshots meet deletion criteria'
    else:
        return output
