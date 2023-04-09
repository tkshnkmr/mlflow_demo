import xgboost as xgb
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)
from sklearn.model_selection import train_test_split

import mlflow
import mlflow.xgboost
from mlflow.models.signature import infer_signature
from hyperopt import (
    fmin, 
    hp, 
    tpe, 
    rand, 
    SparkTrials, 
    Trials, 
    STATUS_OK
)
from hyperopt.pyll.base import scope
from config import TRAIN_RANDOM_SEED, DATASPLIT_SEED


# Setting search space for xgboost model
search_space = {
    'objective': 'reg:squarederror',
    'max_depth': scope.int(hp.quniform('max_depth', 4, 15, 1)),
    'learning_rate': hp.loguniform('learning_rate', -7, 0),
    'reg_alpha': hp.loguniform('reg_alpha', -10, 10),
    'reg_lambda': hp.loguniform('reg_lambda', -10, 10),
    'gamma': hp.loguniform('gamma', -10, 10),
    'use_label_encoder': False,
    'verbosity': 0,
    'random_state': TRAIN_RANDOM_SEED
}
 
try:
    EXPERIMENT_ID = mlflow.create_experiment('xgboost-hyperopt')
except:
    EXPERIMENT_ID = dict(mlflow.get_experiment_by_name('xgboost-hyperopt'))['experiment_id']

def train_model(params):
    """
    Creates a hyperopt training model funciton that sweeps through params in a nested run
    Args:
        params: hyperparameters selected from the search space
    Returns:
        hyperopt status and the loss metric value
    """
    # With MLflow autologging, hyperparameters and the trained model are automatically logged to MLflow.
    # This sometimes doesn't log everything you may want so I usually log my own metrics and params just in case
    mlflow.xgboost.autolog()

    # 
    with mlflow.start_run(experiment_id=EXPERIMENT_ID, nested=True):
        # Training xgboost classifier
        model = xgb.XGBRegressor(**params)
        model = model.fit(X_train, y_train)

        # Predicting values for training and validation data, and getting prediction probabilities
        y_train_pred = model.predict(X_train)
        y_val_pred = model.predict(X_val)

        # Evaluating model metrics for training set predictions and validation set predictions
        # Creating training and validation metrics dictionaries to make logging in mlflow easier
        metric_names = ['mse', "mae"]
        # Training evaluation metrics
        train_mse = mean_squared_error(y_train, y_train_pred).round(3)
        train_mae = mean_absolute_error(y_train, y_train_pred).round(3)

        training_metrics = {
            'Mean Squared Error': train_mse,
            'Mean Absolute Error': train_mae,  
        }
        training_metrics_values = list(training_metrics.values())

        # Validation evaluation metrics
        val_mse = mean_squared_error(y_val, y_val_pred).round(3)
        val_mae = mean_absolute_error(y_val, y_val_pred).round(3)

        validation_metrics = {
            'Mean Squared Error': val_mse,
            'Mean Absolute Error': val_mae,  
        }
        validation_metrics_values = list(validation_metrics.values())
        
        # Logging model signature, class, and name
        signature = infer_signature(X_train, y_val_pred)
        mlflow.xgboost.log_model(model, 'model', signature=signature)
        mlflow.set_tag('estimator_name', model.__class__.__name__)
        mlflow.set_tag('estimator_class', model.__class__)

        # Logging each metric
        for name, metric in list(zip(metric_names, training_metrics_values)):
            mlflow.log_metric(f'training_{name}', metric)
        for name, metric in list(zip(metric_names, validation_metrics_values)):
            mlflow.log_metric(f'validation_{name}', metric)

        # Set the loss to -1*validation auc roc so fmin maximizes the it
        return {'status': STATUS_OK, 'loss': -1*validation_metrics['Mean Squared Error']}

# model training
# Split Features and Labels
X = df.drop(['AveRooms', 'MedHouseVal'], axis=1)
y = df['MedHouseVal']


# Split the data for train (80%) and validation (20%)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=DATASPLIT_SEED)


# Greater parallelism will lead to speedups, but a less optimal hyperparameter sweep.
# A reasonable value for parallelism is the square root of max_evals.
# spark_trials = SparkTrials()
# Will need spark configured and installed to run. Add this to fmin function below like so:
# trials = spark_trials
trials = Trials()

# Run fmin within an MLflow run context so that each hyperparameter configuration is logged as a child run of a parent
# run called "xgboost_models" .
with mlflow.start_run(experiment_id=EXPERIMENT_ID, run_name='xgboost_models'):
    xgboost_best_params = fmin(
        fn=train_model, 
        space=search_space, 
        algo=tpe.suggest,
        trials=trials,
        max_evals=50
    )