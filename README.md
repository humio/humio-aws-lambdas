# humio-aws-lambdas

This repository is a _beta_ initial release of a growing set of AWS lambda functions that facilitate data ingest from various AWS services into Humio.

For CloudWatch logs & metrics integration, please refer to the [cloudwatch2humio](https://github.com/humio/cloudwatch2humio) project.

## Vision

The goal of the `humio-aws-lambdas` Humio project is to create a simple, easy to manage and use lambda to ingest select AWS data into Humio.

## Current Supported Integrations

- `GuardDutyViaCloudWatch`: GuardDuty via CloudWatch Events
- `S3JSON`: JSON object per line, via S3
- `S3Raw`: Raw text, per line, via S3

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

#### Configuration

In addition to the universal environment variables specified above, to enable the `GuardDutyViaCloudWatch` module for GuardDuty integration via CloudWatch, the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `GuardDutyViaCloudWatch`

Apart from this, no further specific configuration is required for this integration module.  Typically, the Lambda trigger will be set up via a CloudWatch event rule (e.g., `source` of `aws.guardduty`, `detail-type` of `GuardDuty Finding`, etc.).

### S3JSON

The `S3JSON` module is used with a trigger on `PUT` to an S3 bucket, and expects data formatted as one JSON object per line.

When a `PUT` operation to an S3 bucket triggers the `S3JSON` module, it streams the newly-put S3 object in, reading it line-by-line as it streams, sending events in batches.

#### Configuration

In addition to the universal environment variables specified above, to enable the `S3JSON` module the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `S3JSON`

Optionally, you may tune the batch size this module uses:

Key | Description
-------- | -----------
HumioS3JSONBatchSize | _Integer values only_, representing the size of event batches it sends to a Humio HEC endpoint, e.g. `20000`.  Default value is `10000`.

### S3Raw

The `S3Raw` module is used with a trigger on `PUT` to an S3 bucket, and expects data to be newline-delimited free text.

When a `PUT` operation to an S3 bucket triggers the `S3Raw` module, it streams the newly-put S3 object in, reading it line-by-line as it streams, sending events in batches.

#### Parsing Consideration

By default, when raw text is supplied to ingest, the default parser is `kvparser` for `key=value` pairs.  To use a different parser, [do so through a new ingest token](https://docs.humio.com/ingesting-data/ingest-tokens/) (in particular, [assigning parsers to ingest tokens](https://docs.humio.com/ingesting-data/parsers/assigning-parsers-to-ingest-tokens/)).

#### Configuration

In addition to the universal environment variables specified above, to enable the `S3Raw` module the following environment variable must be set:

Key | Value
-------- | -----------
HumioAWSModule | `S3Raw`

Optionally, you may tune the batch size this module uses:

Key | Description
-------- | -----------
HumioS3RawBatchSize | _Integer values only_, representing the size of event batches it sends to a Humio HEC endpoint, e.g. `20000`.  Default value is `10000`.


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