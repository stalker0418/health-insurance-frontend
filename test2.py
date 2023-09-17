from taipy import Config, Scope
import pandas as pd
from prophet import Prophet
from functions import *
from functions_claim import *


# Input Data Nodes
initial_dataset_cfg = Config.configure_data_node(id="initial_dataset",
                                                 storage_type="csv",
                                                 default_path='df.csv')

new_person_claim_cfg = Config.configure_data_node(id="new_person",
                                                  default_data = pd.DataFrame({
                                                                    'Procedure_Code': ['CPT456'],
                                                                    'Diagnosis_Code': ['ICD-10-B'],
                                                                    'Provider_Specialty': ['Orthopedics'],
                                                                    'Patient_Age': [35],
                                                                    'Insurance_Plan': ['PPO'],
                                                                    'Deductible': [200],
                                                                    'Copayment': [30],
                                                                    'Coinsurance': [20],
                                                                }, index=[0]))

cleaned_dataset_cfg = Config.configure_data_node(id="cleaned_dataset")



clean_data_task_cfg = Config.configure_task(id="clean_data_task",
                                            function=clean_data,
                                            input=initial_dataset_cfg,
                                            output=cleaned_dataset_cfg,
                                            skippable=True)

clean_data_claim_task_cfg = Config.configure_task(id = "clean_claim_data_task",
                                                  function = clean_data_claim,
                                                  input = [initial_dataset_cfg,new_person_claim_cfg],
                                                  output = cleaned_dataset_cfg,
                                                  skippable = True)


model_training_cfg = Config.configure_data_node(id="model_output")    

predictions_cfg = Config.configure_data_node(id="predictions")





model_training_task_cfg = Config.configure_task(id="model_retraining_task",
                                                function=retrained_model,
                                                input=cleaned_dataset_cfg,
                                                output=model_training_cfg,
                                                skippable=True)

model_training_claim_task_cfg = Config.configure_task(id="model_retraining_claim_task",
                                                      function = retrained_model_claim,
                                                      input = cleaned_dataset_cfg,
                                                      output=model_training_cfg,
                                                      skippable=True)



predict_task_cfg = Config.configure_task(id="predict_task",
                                         function=predict,
                                         input=model_training_cfg,
                                         output=predictions_cfg,  
                                         skippable=True)

predict_claim_task_cfg = Config.configure_task(id="predict_claim_task",
                                               function = predict_claim,
                                               input = [model_training_cfg,new_person_claim_cfg],
                                               output = predictions_cfg,
                                               skippable=True)


# Create the first pipeline configuration
# retraining_model_pipeline_cfg = Config.configure_pipeline(
#     id="model_retraining_pipeline",
#     task_configs=[clean_data_task_cfg, model_training_task_cfg],
# )


# Run the Taipy Core service
# import taipy as tp

# # Run of the Taipy Core service
# tp.Core().run()

# # Create the pipeline
# retrain_pipeline = tp.create_pipeline(retraining_model_pipeline_cfg)

# # Submit the pipeline
# tp.submit(retrain_pipeline)


# tp.Core().stop()

scenario_cfg = Config.configure_scenario_from_tasks(id="stock",
                                                    task_configs=[clean_data_task_cfg,
                                                    model_training_task_cfg,
                                                    predict_task_cfg])

scenario_claim_cfg = Config.configure_scenario_from_tasks(id="claim",
                                                          task_configs=[clean_data_claim_task_cfg,
                                                                        model_training_claim_task_cfg,
                                                                        predict_claim_task_cfg])


# tp.Core().run()
# tp.submit(scenario_cfg)

Config.export("config_model_train.toml")