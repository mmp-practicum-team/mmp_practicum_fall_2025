import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ensembles.backend import ExperimentConfig
from ensembles.frontend import Client, plot_learning_curves

load_dotenv()
BASE_URL = os.environ["BASE_URL"]
MODEL_OPTIONS = ["Random Forest", "Gradient Boosting"]
MAX_FEATURES_OPTIONS = ["all", "sqrt", "log2", "custom integer", "custom float"]


@st.cache_data
def load_data(file):
    return pd.read_csv(file)


client = Client(BASE_URL)

st.title("Model Training and Prediction")

# Sidebar for experiment selection
experiment_option = st.sidebar.selectbox(
    "Experiment", options=["start new"] + client.get_names()
)

if experiment_option == "start new":
    with st.sidebar:
        experiment_name = st.text_input(
            "Give a name to your experiment", value="happy_fox"
        )
        if experiment_name in client.get_names():
            st.error(
                f"Experiment with name {experiment_name} already exists. Choose a different name."
            )

        model_choice = st.selectbox("Choose a model", options=MODEL_OPTIONS)
        n_estimators = st.number_input("Number of estimators", min_value=1, value=100)
        max_depth = st.number_input("Max depth", min_value=1, value=15)
        max_features = st.selectbox("Max features", options=MAX_FEATURES_OPTIONS)
        if max_features == "custom float":
            max_features = st.number_input(
                "Enter custom value", min_value=0.0, max_value=1.0, format="%.2f"
            )
        elif max_features == "custom integer":
            max_features = st.number_input(
                "Enter custom value", min_value=1, format="%d"
            )

        st.header("Upload Training Data")
        train_file = st.file_uploader("Upload your training CSV file", type=["csv"])

        target_column = None
        if train_file is not None:
            train_data = load_data(train_file)
            target_column = st.sidebar.selectbox(
                "Select target column", train_data.columns
            )

        submitted = st.button("Register Experiment")

        if submitted:
            # Re-validate the experiment name at submission time
            if experiment_name in client.get_names():
                st.error(f"Cannot register: Experiment '{experiment_name}' already exists!")
            elif train_file is None:
                st.warning("You didn't load training data yet")
            else:
                experiment_config = ExperimentConfig(
                    name=experiment_name,
                    ml_model=model_choice,
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    max_features=max_features,
                    target_column=target_column,
                )
                client.register_experiment(experiment_config, train_file)
                st.sidebar.success(
                    f"Experiment {experiment_config.name} was successfully created! Refresh the page to see it in the list of experiments"
                )

    st.stop()

# Load existing experiment
experiment_config = client.load_experiment_config(experiment_option)

# Display experiment parameters
with st.sidebar:
    st.selectbox(
        "Choose a model",
        options=MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(experiment_config.ml_model),
        disabled=True,
    )
    st.number_input(
        "Number of estimators",
        min_value=1,
        value=experiment_config.n_estimators,
        disabled=True,
    )
    st.number_input(
        "Max depth", min_value=1, value=experiment_config.max_depth, disabled=True
    )
    st.text_input("Max features", value=experiment_config.max_features, disabled=True)

# Training
response = client.session.get(
    f"{BASE_URL}/needs_training", params={"experiment_name": experiment_config.name}
)
response.raise_for_status()

if response.json()["response"]:
    st.info(
        "The model wasn't trained for the selected experiment yet. Train it to see learning curves and infer on your data."
    )
    if st.button("Train Model"):
        with st.spinner("Training model..."):
            client.train_model(experiment_config.name)
    else:
        st.stop()

# visualize
st.subheader("Learning Curves")
convergence_history = client.get_convergence_history(experiment_config.name)
st.plotly_chart(plot_learning_curves(convergence_history))

# Predict on test data
st.subheader("Inference on your data")
test_file = st.file_uploader("Upload your test CSV file", type=["csv"])

if test_file is not None:
    with st.spinner("Making predictions..."):
        predictions = client.predict(experiment_config.name, test_file)
    st.write(predictions)
