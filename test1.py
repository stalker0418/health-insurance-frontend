from taipy.gui import Gui, notify
import pandas as pd
import yfinance as yf
from taipy.config import Config
import taipy as tp 
import datetime as dt
from taipy import Core
from flask import Flask, request, session, jsonify, redirect, render_template
from flask_restful import Api, Resource
import requests

Config.load("config_model_train.toml")
scenario_cfg = Config.scenarios['stock']
scenario_claim_cfg = Config.scenarios['claim']
tickers = yf.Tickers("msft aapl goog")


root_md = "<center><|navbar|></center>"

property_chart = {
    "type": "lines",
    "x": "AGE",
    "y[1]": "CHARGES",
    "color[1]": "green",
}


prediction_chart = {
    "type": "bar",
    "x": "Date",
    "y[1]": "Close_Prediction",
    "color[1]": "green",
}
df = pd.DataFrame([], columns=["Date", "High", "Low", "Open", "Close"])
df_pred = pd.DataFrame([], columns = ['Date','Close_Prediction'])



df_claim_new_data = pd.DataFrame([], columns=["Procedure_Code", "Diagnosis_Code","Provider_Speciality","Patient_Age","Insurance_Plan","Deductible","Copayment","Coinsurance","Claim_Amount"])
df_claim_data = pd.read_csv('healthcare_billing_dataset.csv')

df_insurance_data = pd.read_csv('insurance.csv')
df_insurance_full_data = pd.read_csv('insurance.csv')


grouped = df_insurance_data.groupby('INSURANCE_COMPANY')
dataframes_dict = {}
for company, group in grouped:
    dataframes_dict[company] = group.reset_index(drop=True)  # Reset the index for each group


df_insurance_data = pd.DataFrame([], columns=["AGE","CHARGES"])

stock = ""
prediction_stock = ""
stock_text = """No Insurance Company is selected"""
chart_text = "No Insurance Company is selected"
prediction_text = "The predicted values are"

procedure_code_text,procedure_code_columns,procedure_code  = "Your Procedure Code", sorted(df_claim_data['Procedure_Code'].unique().tolist()), ""
diagnosis_code_text,diagnosis_code_columns,diagnosis_code  = "Your Diagnosis Code", sorted(df_claim_data['Diagnosis_Code'].unique().tolist()), ""
provider_speciality_text,provider_speciality_columns,provider_speciality  = "Your Provider Speciality", sorted(df_claim_data['Provider_Specialty'].unique().tolist()), ""
patient_age_text,patient_age_columns,patient_age  = "Your age", sorted(df_claim_data['Patient_Age'].unique().tolist()), ""
insurance_plan_text,insurance_plan_columns,insurance_plan  = "Your Insurance Plan", sorted(df_claim_data['Insurance_Plan'].unique().tolist()), ""
deductible_text,deductible_columns,deductible  = "Deductible", sorted(df_claim_data['Deductible'].unique().tolist()), ""
copayment_text,copayment_columns,copayment  = "Your Copayment", sorted(df_claim_data['Copayment'].unique().tolist()), ""
coinsurance_text,coinsurance_columns,coinsurance  = "Your Coinsurance", sorted(df_claim_data['Coinsurance'].unique().tolist()), ""

output_claim = ""
 

page = """
## <center>Insurance Predictor</center>
<center>-----------------------------------------------------------------------------------------------------------------------------------------------</center>
<|toggle|theme|>
<|layout|columns=1 1|
<|
### Choose the Insurance Plan to see the pricing trends



<|{stock_text}|>

<|{stock}|selector|lov=NSO;ESO;SEO;SWO;Reset|dropdown|>
<br/>
<|Press for the Price Comparision|button|on_action=on_button_action|>
<|&nbsp;|><|&nbsp;|><|&nbsp;|><|&nbsp;|><|&nbsp;|>
<|Get the future predictions|button|on_action=get_predictions|>
|>
|>
<|
<|{stock}
<|{chart_text}|>
<|{df_insurance_data}|chart|properties={property_chart}|>
|>

|>




<|
|>

"""
show1 = False
explore_page = """
<|toggle|theme|>
##<center>Summary of the insurance and their perks</center>
-----------------------------------------------------------------------------------------------------
<br/><br/><br/><br/>

<|{df_insurance_full_data}|table|width=100%|>







"""


claim_page = """

### <center>Predict your claim amount</center> 
<|toggle|theme|>

<|layout|columns=1 1 1|
<|
<|{procedure_code_text}|>
<|{procedure_code}|selector|lov={procedure_code_columns}|dropdown|>
|>
<|
<|{diagnosis_code_text}|>
<|{diagnosis_code}|selector|lov={diagnosis_code_columns}|dropdown|>
|>
<|
<|{provider_speciality_text}|>
<|{provider_speciality}|selector|lov={provider_speciality_columns}|dropdown|>
|>
|>

<|layout|columns=1 1 1|
<|
<|{patient_age_text}|>
<|{patient_age}|selector|lov={patient_age_columns}|dropdown|>
|>
<|
<|{insurance_plan_text}|>
<|{insurance_plan}|selector|lov={insurance_plan_columns}|dropdown|>
|>
<|
<|{deductible_text}|>
<|{deductible}|selector|lov={deductible_columns}|dropdown|>
|>
|>

<|layout|columns=1 1 1|
<|
<|{copayment_text}|>
<|{copayment}|selector|lov={copayment_columns}|dropdown|>
|>
<|
<|{coinsurance_text}|>
<|{coinsurance}|selector|lov={coinsurance_columns}|dropdown|>
|>
|>
<br/><br/>
<|Predict the Amount I can claim|button|on_action=on_button_claim_action|>

    



"""
    


pages = {
    "/" : root_md,
    "home" : page,
    "claim": claim_page,
    "near_me": """##Nearest Hospitals that can be claimable by your insurance are as follows:""",
    "explore": explore_page
}

def on_button_action(state):
    if state.stock == "Reset":
        state.stock_text = "Nothing to Show"
        state.chart_text = "Nothing to Show"
        state.df_insurance_data = pd.DataFrame([], columns=["AGE", "CHARGES"])
        state.df_pred = pd.DataFrame([], columns = ['Date','Close_Prediction'])
        state.pred_text = "No Prediction to Show"
    else:
        state.stock_text = f"The selected insurance  is {state.stock}"
        state.chart_text = f"Yearly history of pricing for the selected insurance {state.stock}"
        # state.df = tickers.tickers[state.stock].history().reset_index()
        state.df_insurance_data = dataframes_dict[state.stock]
        state.df.to_csv(f"{stock}.csv", index=False)




def get_predictions(state,name):

    if state.stock == "Reset":
        state.prediction_text = "No Prediction to show"
    else:
        state.prediction_text = f"The prediction values of {state.stock} for the next year are"
    
    scenario_stock = tp.create_scenario(scenario_cfg)
    scenario_stock.initial_dataset.path = f"{state.stock}.csv"
    
    scenario_stock.initial_dataset.write(state.df)
    tp.submit(scenario_stock)
    state.df_pred = scenario_stock.predictions.read()
    notify(state, 'success', f"successfully predicted the values for the next month for {state.stock}")
    state.df_pred.to_csv("pred.csv", index=False)



def on_button_claim_action(state):
    new_patient_data = pd.DataFrame({
                                    'Procedure_Code': state.procedure_code,
                                    'Diagnosis_Code': state.diagnosis_code,
                                    'Provider_Specialty': state.provider_speciality,
                                    'Patient_Age': state.patient_age,
                                    'Insurance_Plan': state.insurance_plan,
                                    'Deductible': state.deductible,
                                    'Copayment': state.copayment,
                                    'Coinsurance': state.coinsurance,
                                }, index=[0])
   
    # notify(state,'success', f"Successfully read the values{state.coinsurance}")
    new_patient_data.to_csv("new_person_data.csv", index=False)

    scenario_claim = tp.create_scenario(scenario_claim_cfg)
    scenario_claim.initial_dataset.path = "healthcare_billing_dataset.csv"
    scenario_claim.new_person.write(new_patient_data)

    tp.submit(scenario_claim)
    state.output_claim = scenario_claim.predictions.read()['claim']
    notify(state, "success", f"Congrats!!! You can claim ${state.output_claim[0][0]:.2f}")

def show1toggle(state):
    state.show11 = not state.show1

tp.Core().run()

app = Flask(__name__)
# app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management
api = Api(app)
class SignupResource(Resource):
    def get(self):
        return redirect("/signup.html")
    
    def post(self):
        SIGNUP_API_URL = "https://health-insurance-rest-apis.onrender.com/api/signup"
        signup_data = {
            'username': request.form['username'],
            'password': request.form['password'],
            'email': request.form['email']
        }
        headers = {
            'Content-Type': 'application/json'
        }
        print(signup_data)
        response = requests.post(SIGNUP_API_URL, headers=headers, json=signup_data)
        print("response", response)
        if response.status_code == 200:
            return redirect("/login.html")
        else:
            return 'Signup Failed'

# Login Resource
class LoginResource(Resource):
    def get(self):
        """
        Return a simple login page HTML
        """
        return redirect("/login.html")
    def post(self):
        email = request.form['email']
        password = request.form['password']
        auth_data = {
            'username': email,
            'password': password
        }
        AUTH_API_URL = "https://health-insurance-rest-apis.onrender.com/api/login"
        response = requests.post(AUTH_API_URL, json=auth_data)
        if response.status_code == 200:
            auth_data = response.json()
            access_token = auth_data.get('access_token')
            refresh_token = auth_data.get('refresh_token')

            # Store tokens in the session
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token

            url = "https://dev-77es4fksvluam0eo.us.auth0.com/userinfo"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Parse the JSON content from the response
                json_data = response.json()

                # Access specific keys from the JSON data
                if 'email' in json_data:
                    user_name = json_data['email']
                    print(f"The value of 'email' is: {user_name}")
                else:
                    print("'email' not found in the JSON data")
            else:
                # Handle the error if the request was not successful
                print(f"Request failed with status code {response.status_code}")

            return redirect(f"/home?email={user_name}")
        else:
            return 'Login failed', 401


# Protected Resource
class ProtectedResource(Resource):
    def get(self):
        # Check if the JWT token is present in the session
        if 'jwt_token' in session:
            jwt_token = session['jwt_token']

            # You can add logic here to verify the JWT token if needed
            # For simplicity, we assume the token is valid

            return {'message': 'Access granted for protected route', 'jwt_token': jwt_token}, 200
        else:
            return {'message': 'Access denied'}, 401

print("registered the apis")
# Add resources to the API
api.add_resource(LoginResource, '/login')
api.add_resource(ProtectedResource, '/protected')
api.add_resource(SignupResource, '/signup')

@app.before_request
def check_access_token():
    # print ('access_token' in session, "checkIt")
    if request.endpoint != 'login' and 'access_token' not in session:
    #     # Redirect to the login page if not on the login route and no access_token is in the session
    #     print(request.endpoint, "endpoint")
        return redirect("/login")

gui = Gui(pages=pages, flask=app).run(debug=False)




