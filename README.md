# SimpleWebScraper

This is a web scraping project intended to be deployed and run in the AWS cloud.

## Preliminaries
 - Install [Git](https://git-scm.com/downloads)
 - Install [Google Chrome](https://www.google.com/chrome/)
 - Install [Python](https://www.python.org/downloads/release/python-3112/) (**Tick yes for adding Python to your path!**)
 - Install [Visual Studio Code](https://code.visualstudio.com/Download) with the Python extension
 - Install [Docker](https://www.docker.com/products/docker-desktop/)
 - Setup a [free AWS account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)
 - [Clone this repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) to your local machine

## Useful Commands for the Demo
You can navigate to a directory using _cd_ and then the name of the directory. You will need to navigate to where you want to clone this directory

pip install -r .\requirements.txt

docker build -t _name_ .

docker tag _name_:latest public.ecr.aws/_dir_/_name_:latest

docker push public.ecr.aws/_dir_/_name_:latest

- For ECS permissions:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
