# NeurotechX 2020 Student Clubs Competition Submission

## Project Overview

## Project Setup

### Acquiring Data
In order to have multiple people work on the project more easily, we decided to use an EEG dataset as our input for our BCI rather than streaming the data.
 
Specifically, we used a 2 minute long recording from our 2016 Muse headset acquired from the Mind Monitor app. After turning on the Muse and opening the app, the Muse headset should automatically connect to your cellphone. The light on the Muse will stop blinking and become solid once connected. Any other Muse-related app cannot be open during this time or the connection to Mind Monitor will not work. During the first minute of the recording, the participant closed their eyes and relaxed, and we used this data as our baseline. During the second minute, the participant counted backwards from 2064 by 7s in their head. The participant did not speak out loud in order to prevent unnecessary jaw movement that would affect the EEG data. The data was saved as a .csv file with a 256 Hz sampling rate.

### Processing the Data
Before running the Python script, make sure that Python is installed, along with the ```pandas```, ```numpy```, ```scipy```, and ```requests``` libraries. The libraries can be installed with pip or any other package manager. Open the script in a text editor of your choice and edit line #63 with the path to your file, i.e. 
```
data = pd.read_csv('path/to/your/file', ...)
```
Also make sure to change line #131 if your proxy url is different.

Once these changes are made, run the script. If you refresh DynamoDB, you should see the values changing every few seconds.

### DynamoDB Setup
For our Python script to communicate with the web application, we have to make use a database. Our database of choice was DynamoDB, and we'll see that this greatly simplifies the setup required for our other components. Go to the [AWS Console](https://aws.amazon.com/console/). Once you sign in, find the DynamoDB service and click on it. From the console, you can create a table by specifying a table name and the primary key. The name of the table can be anything you desire, but the primary key should be ```type```. This essentially specifies that each item that is stored in the database must have an attribute called ```type```. In our case, the possible values of ```type``` are ```alpha```, ```beta```, and ```alphaAsymmetry```. For our purposes, we can use the default settings. 

### API Gateway Setup
Once the table is created, go back to the AWS console and search for the IAM service, which allows us to create specific roles tied to the account that have specific permissions. It is highly recommended that you follow this step. Go to the Roles tab and create a new role. For the use case, select API Gateway and hit the next button until you reach the last form page, which requires a name for the role. Once the role is created, click on it and click the ```Attach policies``` button. Search for ```AmazonDynamoDBFullAccess``` and attach it to the role.

Once that's done, we can go back to the AWS console and click on the API Gateway service. Create a new REST API by going through the creation wizard. Once the API has been created, click on ```Actions > Create Resource```. Create a new resource called type, and specify the resource path as ```/{type}```. The curly braces specify a path variable, which allows us to make specific queries based on the url that we request from. Make sure that CORS is enabled before creating the resource. Now, we can create the methods to access these resources. We are interested in ```GET``` and ```PUT``` methods, which query for and update resources, respectively. We will first create the ```GET``` method. Select AWS Service as the Integration type. Set the region as the region that your DynamoDB table is in and set the AWS Service to DynamoDB. For the HTTP Method, we specify ```POST```. While this may seem strange, this is how queries to DynamoDB are made. Set the action as ```GetItem```; this is how we will let DynamoDB know that we're interested in retrieving a resource. For the execution role, go to the role that you created in the previous section and copy the Role ARN. 

Once the method is created, there will be a diagram that illustrates how data is transferred between the Client and DynamoDB. Go to ```Integration Request > Mapping Templates```. Set the request body passthrough option to the recommended one and then click on Add mapping template. The template should be called ```application/json```. Copy the following into the template: 
```
{
  "TableName": "brainwavePowerPercentages",
  "Key": {
    "type": {
      "S": "$input.params('type')"
    }
  }
}
```

Note that TableName may differ. Once that is done, save your changes and then go back to the Method Execution screen. If you've added elements to the DynamoDB table via the console already, you should be able to query for them if you specify the type. However, we can see from the output that it is not in the cleanest format. To change our output format, we can go to ```Integration Response > Method response status=200 > Mapping Templates > application/json```. Copy the following into the template: 
```
{
  "type": "$input.path('$.Item.type.S')",
  "value": "$input.path('$.Item.value.N')"
}
```

Once we go back and test our method again, we can see that the output has a cleaner format. 

Repeat the previous steps for our ```PUT``` method. The only changes are the action, which should be ```PutItem```, and the Integration Request template, which is shown below:
```
{
    "TableName": "brainwavePowerPercentages",
    "Item": {
    	"type": {
            "S": "$input.params('type')"
        },
        "value": {
            "N": "$input.path('$.value')"
        }
    }
}
```

Note that ```PUT``` does not have an expected response and that along with providing the ```type``` parameter, a ```value``` parameter should also be sent as data. 

Once both methods have been created, deploy the API. Once it is deployed, the information page will have an invoke URL. Copying that link and adding a ```/alpha```, ```/beta```, or ```/alphaAsymmetry```will give us the value corresponding to that resource in the table. 

### Proxy Setup
Because our web app is running locally, we will need a proxy to bypass CORS, a mechanism that restricts requests between websites on different domains without propery verification. While this is not a good idea for real applications, it is sufficient for a prototype. Follow the tutorial [here](https://www.npmjs.com/package/local-cors-proxy) to set up the proxy. 

### Running the Web Application
Running the React app requires Node, which can be downloaded [here](https://nodejs.org/en/download/). Once Node is installed, navigate to the directory containing the code for the app (package.json should be one of the files listed). Run the command ```npm install``` to install all the dependencies, then run ```npm start``` to run the app locally. Running the latter command should open up a tab in your default browser immediately, but if it does not, go to the url ```localhost:3000```. 

## Conclusion
Although we had to adapt due to the far-reaching impacts of the COVID-19 pandemic, we developed a system that can detect and visualize changes in alpha and beta powers as well as alpha asymmetry values from raw EEG data. For the future, we aim to add detection of eye blinks or jaw clenches to our system so that they can be removed from the signal. We also aim to find and remove streamed EEG values that are too noisy due to momentary movement or loss of contact between the electrode and participant. In addition, we could explore other signal processing methods such as wavelet transformations.

In the future, we could develop a more formal feedback system based on this project. As mentioned earlier, alpha asymmetry values can be indicative of negative thinking. We could provide participants with a variety of visual feedback that corresponds to their asymmetry values to help them train their brain toward more left-sided brain activity. Testing this with many participants over multiple sessions and seeing how asymmetry values change would be a really cool experiment!
