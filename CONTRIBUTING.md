# Contributing
Contributions are welcome, and they are greatly appreciated! 
Every little bit helps, and credit will always be given.

## Ways To Contribute
There are many different ways, in which you may contribute to this project, including:

   * Opening issues by using the [issue tracker](https://github.com/humio/aws-lambdas/issues), using the correct issue template for your submission.
   * Commenting and expanding on open issues.
   * Propose fixes to open issues via a pull request.

We suggest that you create an issue on GitHub before starting to work on a pull request, as this gives us a better overview, and allows us to start a conversation about the issue.
We also encourage you to separate unrelated contributions into different pull requests. This makes it easier for us to understand your individual contributions and faster at reviewing them.

## Setting Up aws-lambdas For Local Development

Following is described how to set up the integration for local development. 

### Prerequisites

* AWS CLI installed and setup with an AWS account that has the appropriate 
permissions.
* Python 3.x installed.

### Setup

1. Clone the git repository: [https://github.com/humio/aws-lambdas](https://github.com/humio/aws-lambdas).

2. In the project folder, build an AWS Lambda-ready `.zip` file:
      
      This is done by using the present makefile: 
      
      ```
      $ make
      ```

3. Upload to an S3 bucket of your choosing.
4. Using the AWS console, set up an instance of the Humio AWS Lambda according to the README for the specific integration required.

## Making A Pull Request
When you have made your changes locally, or you want feedback on a work in progress, you're almost ready to make a pull request. Before doing so however, please go through the following checklist:

1. Write new test cases if the old ones do not cover your new code.   
2. Run the tests locally and check that they pass
3. Add yourself to ``AUTHORS.md``.

When you've been through the the checklist, push your final changes to your development branch on GitHub.

Congratulations! Your branch is now ready to be included submitted as a pull requests. Go to [aws-lambdas](http://github.com/humio/aws-lambdas) and use the pull request feature to submit your contribution for review.

Terms of Service For Contributors
=================================
For all contributions to this repository (software, bug fixes, configuration changes, documentation, or any other materials), we emphasize that this happens under GitHubs general Terms of Service and the license of this repository.

## Contributing as an individual
If you are contributing as an individual you must make sure to adhere to:

The [GitHub Terms of Service](https://help.github.com/en/github/site-policy/github-terms-of-service) __*Section D. User-Generated Content,*__ [Subsection: 6. Contributions Under Repository License](https://help.github.com/en/github/site-policy/github-terms-of-service#6-contributions-under-repository-license):

_"Whenever you make a contribution to a repository containing notice of a license, you license your contribution under the same terms, and you agree that you have the right to license your contribution under those terms. If you have a separate agreement to license your contributions under different terms, such as a contributor license agreement, that agreement will supersede.
Isn't this just how it works already? Yep. This is widely accepted as the norm in the open-source community; it's commonly referred to by the shorthand "inbound=outbound". We're just making it explicit."_

## Contributing on behalf of a Corporation
If you are contributing on behalf of a Corporation you must make sure to adhere to:

The [GitHub Corporate Terms of Service](https://help.github.com/en/github/site-policy/github-corporate-terms-of-service) _**Section D. Content Responsibility; Ownership; License Rights,**_ [subsection 5. Contributions Under Repository License](https://help.github.com/en/github/site-policy/github-corporate-terms-of-service#5-contributions-under-repository-license):

_Whenever Customer makes a contribution to a repository containing notice of a license, it licenses such contributions under the same terms and agrees that it has the right to license such contributions under those terms. If Customer has a separate agreement to license its contributions under different terms, such as a contributor license agreement, that agreement will supersede_