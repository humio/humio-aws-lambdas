# humio-aws-lambdas

This repository is a _beta_ initial release of a growing set of AWS lambda functions that facilitate data ingest from various AWS services into Humio.

For CloudWatch logs & metrics integration, please refer to the [cloudwatch2humio](https://github.com/humio/cloudwatch2humio) project.

## Vision

The goal of the `humio-aws-lambdas` Humio project is to create a simple, easy to manage and use lambda to ingest select AWS data into Humio.

## Current Supported Integrations

- `GuardDutyViaCloudWatch`: GuardDuty via CloudWatch Events
- `S3`: S3, raw text, JSON data handling, or metadata-only events (`S3JSON` & `S3Raw` are _deprecated_ but still functional)
- `Kinesis`: Kinesis, per put record, raw text or JSON
- `SNS`: Simple Notification Service
- `SQS`: Simple Queue Service

## Universal Installation & Configuration

This section describes the universal build and installation procedure for all current `humio-aws-lambdas` integrations.

### Requirements

- Python 3.x

### Building `target/humio-aws-lambdas.zip`

1. Execute `make`.
2. The Lambda-ready `.zip` file is available at `target/humio-aws-lambdas.zip`.

### Basic Lambda Settings

The required AWS Lambda properties are:

Property | Description
-------- | -----------
Runtime | `Python 3.7`
Handler | `HumioLambda.lambda_handler`
Memory | `128` MB
Timeout | `0 min 10sec`

#### Note: `Timeout` & `Memory`

Regarding `Timeout` and `Memory`, different modules may require these values to be increased.  See the "Notes" section at the end of this document for more information.

### Environment Variables

Because this project creates the basis for a stack of lambdas that will power many Humio-AWS integrations, there are both "_universal_" environment variables which apply to _all_ integration components, as well as "_specific_" environment variables that apply to individual integrations.

The universal environment variables are:
- `HumioBaseURL`, the location of the Humio service you're integrating with, 
- `HumioAWSModule`, the Humio integration module that supports the AWS service you're integrating with, and
- the method and details by which the Humio ingest token is retrieved, one of
	- `HumioIngestToken`, the plaintext Humio repo ingest token, or
	- to use the AWS Secrets Manager, using `HumioIngestTokenArn` and `HumioIngestTokenSecret` (see below).

Universal environment variables are described below:

Key | Description
-------- | -----------
HumioAWSModule | This variable's value parameterizes the integration the Lambda instance, e.g., for `GuardDuty` via `CloudWatch` events, you would use the value `GuardDutyViaCloudWatch`.  See the section "Current Integrations" below for specific details on each available integration.
HumioBaseURL | The base URL of your Humio install or cloud endpoint, e.g., `https://cloud.us.humio.com`

#### Environment Variables: Plaintext Ingest Token

Key | Description
-------- | -----------
HumioIngestToken | Plaintext ingest token (e.g., `IRrovFsR9PrgHSVZkmtPZhBWqeprGJOA76Z`)

#### Environment Variables: Ingest Token via Secrets Manager

Key | Description
-------- | -----------
HumioIngestTokenArn | Secret manager ARN for ingest token (e.g., `arn:aws:secretsmanager:us-east-1:...:secret:...`)
HumioIngestTokenSecret | Secret name (e.g., `HUMIO_INGEST_KEY`)


## Current Integrations

This section provides details for each currently supported AWS service integration.

### GuardDutyViaCloudWatch

#### Parsing Consideration

For information on event schema, see the AWS documentation page [CloudWatch event format for GuardDuty](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings_cloudwatch.html#guardduty_findings_cloudwatch_format).

#### Configuration

In addition to the universal environment variables specified above, to enable the `GuardDutyViaCloudWatch` module for GuardDuty integration via CloudWatch, the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `GuardDutyViaCloudWatch`

Apart from this, no further specific configuration is required for this integration module.  Typically, the Lambda trigger will be set up via a CloudWatch event rule (e.g., `source` of `aws.guardduty`, `detail-type` of `GuardDuty Finding`, etc.).

### S3

The `S3` module is used with a trigger on an S3 bucket, and has varying functionality depending on configuration (see below).

#### Parsing Consideration

When an operation to an S3 bucket triggers the `S3` module, in the case of `HumioS3DataType` configuration value being `raw` or `json`, and the S3 operation being a `PUT`, it streams the newly-put S3 object in, reading it line-by-line as it streams, sending events in batches; in the case of `HumioS3DataType` configuration value being `metadata`, typically multiple triggers or a trigger on all S3 operations are used, and only S3 event metadata is sent to Humio (S3 object bodies are not accessed).

Every record ingested via this module will have at least following fields:

Key | Description
--- | -----------
awsRegion | AWS Region, e.g., `us-east-1`
eventName | e.g., `ObjectCreated:Put`
eventSource | `aws:s3`
eventTime | The time, in ISO-8601 format (e.g., `1970-01-01T00:00:00.000Z`) when Amazon S3 finished processing the request.
eventVersion | AWS S3 event version, e.g., `2.1`.
requestParameters.sourceIPAddress | IP address where request came from, e.g., `1.2.3.4`.
responseElements.x-amz-request-id | Amazon S3 generated request ID.
responseElements.x-amz-id-2 | Amazon S3 host that processed the request.
s3.bucket.arn | e.g., `arn:aws:s3:::some-s3-bucket`
s3.bucket.name | e.g., `some-s3-bucket`
s3.bucket.ownerIdentity.principalId | Amazon customer ID of the bucket owner.
s3.configurationId | ID found in the bucket notification configuration.
s3.object.eTag | e.g., `0f3a06bda0647ed09b0f951...`
s3.object.key | e.g., `some-filename.json`
s3.object.sequencer | String representation of a hexadecimal value used to determine event sequence, only used with `PUT` and `DELETE` operations.
s3.object.size | Object size, in bytes, e.g., `8742`
s3.object.versionId | Object version if bucket is versioning-enabled, otherwise not present.
s3.s3SchemaVersion | e.g., `1.0`
userIdentity.principalId | Amazon customer ID of the user who caused the event.
data[.*] | If `HumioS3DataType` is `raw` or `json`, S3 object content is interpreted and is stored in this field.  This field is _not_ present if `HumioS3DataType` is `metadata`.  For more information, see below.

For more information, consult the [Event message structure AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/notification-content-structure.html).

#### Configuration

In addition to the universal environment variables specified above, to enable the `S3JSON` module the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `S3`
HumioS3DataType | This configuration variable may be _one_ of `raw`, `json`, or `metadata`.  In the case of `raw` and `json`, the S3 object is streamed and interpreted, per line, as text or JSON, emitting one event per line; in the case of a value of `metadata`, only the S3 event metadata is sent, one per event (e.g., a `PUT` operation).  Default value is `metadata`.

Optionally, you may specify tune the batch size this module uses:

Key | Description
-------- | -----------
HumioS3BatchSize | _Integer values only_, representing the size of event batches it sends to a Humio HEC endpoint, e.g. `20000`.  Default value is `10000`.

### Kinesis

The `Kinesis` module is used with a trigger on an AWS Kinesis stream.  All Lambda trigger configurations are supported, though they can have varying effects on downstream data.  For more information, read [Using AWS Lambda with Amazon Kinesis
](https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html)

#### Parsing Consideration

By default, when raw text is supplied to ingest, the default parser is `kvparser` for `key=value` pairs.  To use a different parser, [do so through a new ingest token](https://docs.humio.com/ingesting-data/ingest-tokens/) (in particular, [assigning parsers to ingest tokens](https://docs.humio.com/ingesting-data/parsers/assigning-parsers-to-ingest-tokens/)).

If records are put to the Kinesis stream in JSON format, you should use the `HumioKinesisDataType` configuration environment variable, setting it to `json` (see below).

Every record ingested via this module will have the following fields:

Key | Description
--- | -----------
awsRegion | AWS Region, e.g., `us-east-1`
eventID | e.g., `shardId-000000000003:4234496093157802...`
eventName | `aws:kinesis:record`
eventSource | `aws:kinesis`
eventSourceARN | e.g., `arn:aws:kinesis:us-east-1:041844444...:stream/some-kinesis-stream`
eventVersion | AWS Kinesis event version, e.g., `1.0`
invokeIdentityArn | AWS Lambda invocation identity ARN, e.g., `arn:aws:iam::1234...:role/service-role/test-kinesis-lambda-role-prb3lol8ez1`
kinesis.approximateArrivalTimestamp | Approximate message arrival time as determined by AWS Kinesis, e.g., `1595965460.13`
kinesis.data[.*] | When `HumioKinesisDataType` is `json`, the Kinesis message content is interpreted as JSON and the object lives under `kinesis.data...`.  When `HumioKinesisDataType` is `raw`, the text interpretation of the data will live under `kinesis.data`
kinesis.kinesisSchemaVersion | Current Kinesis schema version in use, e.g., `1.0`
kinesis.partitionKey | The value used to assign this message to a Kinesis shard
kinesis.sequenceNumber | Kinesis-assigned [sequence number](https://docs.aws.amazon.com/streams/latest/dev/key-concepts.html).

#### Configuration

In addition to the universal environment variables specified above, to enable the `Kinesis` module the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `Kinesis`

Optionally, you may specify an expected data type to interpret the event payload, or tune the batch size this module uses:

Key | Description
-------- | -----------
HumioKinesisDataType | _One_ of `raw` or `json`.  `raw` causes the Kinesis records to be interpreted as UTF-8 text.  `json` causes the Kinesis records to be interpreted as JSON objects.  Default is `raw`.
HumioKinesisBatchSize | _Integer values only_, representing the size of event batches it sends to a Humio HEC endpoint, e.g. `20000`.  Default value is `10000`.

### SNS

The `SNS` module is used with a trigger on an AWS SNS topic.

#### Parsing Consideration

By default, when raw text is supplied to ingest, the default parser is `kvparser` for `key=value` pairs.  To use a different parser, [do so through a new ingest token](https://docs.humio.com/ingesting-data/ingest-tokens/) (in particular, [assigning parsers to ingest tokens](https://docs.humio.com/ingesting-data/parsers/assigning-parsers-to-ingest-tokens/)).

If events published to the topic have JSON bodies, you should use the `HumioSNSDataType` configuration environment variable, setting it to `json` (see below).

Every record ingested via this module will have at least the following fields:

Key | Description
--- | -----------
Sns.Message[.*] | The body of the SNS message, either as text or as a JSON object, depending on the setting of `HumioSNSDataType` (see below).
Sns.MessageAttributes[.*.Type/Value] | Any attributes attached the SNS message (see [Amazon SNS message attributes](https://docs.aws.amazon.com/sns/latest/dg/sns-message-attributes.html))
Sns.MessageId | From [AWS Documentation](https://docs.aws.amazon.com/sns/latest/dg/sns-message-and-json-formats.html): "A Universally Unique Identifier, unique for each message published. For a notification that Amazon SNS resends during a retry, the message ID of the original message is used."
Sns.Signature | Base64-encoded SHA1withRSA signature of the Message, MessageId, Subject (if present), Type, Timestamp, and TopicArn values.
Sns.SignatureVersion | Version of the Amazon SNS signature used.
Sns.SigningCertUrl | The URL to the certificate that was used to sign the message.
Sns.Subject | Text of SNS message subject
Sns.Timestamp | e.g., `2020-07-29T16:43:36.024Z`
Sns.TopicArn | Topic ARN SNS message was published to, e.g., `arn:aws:sns:us-east-1:01234....:some-topic`
Sns.Type | One of `SubscriptionConfirmation`, `Notification` or `UnsubscribeConfirmation`

#### Configuration

In addition to the universal environment variables specified above, to enable the `Kinesis` module the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `SNS`

Optionally, you may specify an expected data type to interpret the event payload, or tune the batch size this module uses:

Key | Description
-------- | -----------
HumioSNSDataType | _One_ of `raw` or `json`.  `raw` causes the Kinesis records to be interpreted as UTF-8 text.  `json` causes the SNS message body to be interpreted as a JSON object.  Default is `raw`.
HumioSNSBatchSize | _Integer values only_, representing the size of event batches it sends to a Humio HEC endpoint, e.g. `20000`.  Default value is `10000`.

### SQS

The `SQS` module is used with a trigger on an AWS SQS queue.

#### Parsing Consideration

By default, when raw text is supplied to ingest, the default parser is `kvparser` for `key=value` pairs.  To use a different parser, [do so through a new ingest token](https://docs.humio.com/ingesting-data/ingest-tokens/) (in particular, [assigning parsers to ingest tokens](https://docs.humio.com/ingesting-data/parsers/assigning-parsers-to-ingest-tokens/)).

If events published to the topic have JSON bodies, you should use the `HumioSQSDataType` configuration environment variable, setting it to `json` (see below).

Every record ingested via this module will have at least the following fields:

Key | Description
--- | -----------
attributes.ApproximateFirstReceiveTimestamp | The time the message was first received from the queue (epoch time in milliseconds).
attributes.ApproximateReceiveCount | The number of times a message has been received across all queues but not deleted.
attributes.SenderId | For an IAM user, returns the IAM user ID, e.g., `ABCDEFGHI1JKLMNOPQ23R`.  For an IAM role, returns the IAM role ID, e.g., `ABCDE1F2GH3I4JK5LMNOP:i-a123b456`.
attributes.SentTimestamp | The time the message was sent to the queue (epoch time in milliseconds).
awsRegion | e.g., `us-east-1`
body[.*] | The body of the SQS message, either as text or as a JSON object, depending on the setting of `HumioSQSDataType` (see below).
eventSource | `aws:sqs`
eventSourceARN | e.g., `arn:aws:sqs:us-east-1:012345...:some-queue`
md5OfBody | An MD5 digest of the non-URL-encoded message body string.
md5OfMessageAttributes | An MD5 digest of the non-URL-encoded message attribute string. You can use this attribute to verify that Amazon SQS received the message correctly. Amazon SQS URL-decodes the message before creating the MD5 digest.
messageAttributes[.*.dataType/stringValue] | Any attributes attached the SQS message.
messageId | A unique identifier for the message. A MessageIdis considered unique across all AWS accounts for an extended period of time. e.g., `fae08ce4-1234-4a12-437d-7e630983d7fe`
receiptHandle | An identifier associated with the act of receiving the message. A new receipt handle is returned every time you receive a message. When deleting a message, you provide the last received receipt handle to delete the message. e.g., `AQEBe+YFEcv00EQKq1toMPrC1paj0yGQk2Kd/...`

For more information, see AWS documentation entitled [An Amazon SQS Message](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_Message.html).

#### Configuration

In addition to the universal environment variables specified above, to enable the `Kinesis` module the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `SQS`

Optionally, you may specify an expected data type to interpret the event payload, or tune the batch size this module uses:

Key | Description
-------- | -----------
HumioSQSDataType | _One_ of `raw` or `json`.  `raw` causes the Kinesis records to be interpreted as UTF-8 text.  `json` causes the SQS message body to be interpreted as a JSON object.  Default is `raw`.
HumioSQSBatchSize | _Integer values only_, representing the size of event batches it sends to a Humio HEC endpoint, e.g. `20000`.  Default value is `10000`.

## Notes

### Lambda Timeout

When testing these modules, be sure to ensure the lambda execution time limit is long enough to accommodate the greatest data volume you expect to encounter.  This will be different for every system; one option is to, during testing and while monitoring in production, look at CloudWatch logs in the monitoring tab of your lambda, specifically `DurationInMS`, ensuring that value is smaller than your maximum lambda invocation time for any given invocation.  

### Lambda Memory

Like lambda timeout values, available memory may have to be adjusted, depending on your data volumes.  This is adjustable via the "Basic Settings" panel in the lambda console.

### Batch Size

When applicable, increasing module batch sizes (e.g., `HumioS3RawBatchSize`, `HumioS3JSONBatchSize`, etc.) can greatly increase throughput.  This will likely take some balancing with lambda timeout values.

## Governance

This project is maintained by employees at Humio ApS.
As a general rule, only employees at Humio can become maintainers and have commit privileges to this repository.
Therefore, if you want to contribute to the project, which we very much encourage, you must first fork the repository.
Maintainers will have the final say on accepting or rejecting pull requests.
As a rule of thumb, pull requests will be accepted if:
 
   * The contribution fits with the project's vision
   * All automated tests have passed
   * The contribution is of a quality comparable to the rest of the project
 
The maintainers will attempt to react to issues and pull requests quickly, but their ability to do so can vary.
If you haven't heard back from a maintainer within 7 days of creating an issue or making a pull request, please feel free to ping them on the relevant post.

Maintainers will also be in charge of both versioning and publishing future releases of the project. This includes adding versioning tags and adding to the changelog file.
 
The active maintainers involved with this project include:
  
   * [John Muellerleile](http://github.com/jrecursive)