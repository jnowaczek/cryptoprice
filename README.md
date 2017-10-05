# cryptoprice
Alexa skill for fetching Coinbase API spot prices built using the Alexa Skills Kit and powered by AWS Lambda.

## Configuration
To run your own copy of the skill you can follow the directions in this [Alexa Python tutorial](https://developer.amazon.com/alexa-skills-kit/alexa-skill-quick-start-tutorial) with the following changes:
		
* You'll need to add an environment variable named `applicationID` to your Lambda function with the value set to the Application ID displayed in the Alexa Skill Developer Console.
* This skill is written in Python 3, so make sure your Lambda function's language is set accordingly.
* Replace the intent schema in the tutorial with the contents of [InteractionModel.json](InteractionModel.json).
* Since this skill uses packages not found in the default Lambda environment, you'll need to [package the Python file](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) to include the proper dependencies. After doing this once, you can use the inline editor to make further changes.
