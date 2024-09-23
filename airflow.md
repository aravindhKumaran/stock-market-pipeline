# Airflow Internal Workflow:

## Creating a DAG file:
- A DAG file is created in the dags directory, defining tasks, their dependencies, and schedules.

## Scheduler scans and parses the DAG file:
- The Airflow scheduler periodically (default is every 5 minutes, configurable via scheduler.dag_dir_list_interval) scans the dags directory, reads new or updated DAG files, and parses them to understand the task definitions and dependencies.

## Scheduler serializes the DAG and stores it in the metadata database:
- Once parsed, the scheduler serializes the DAG (converting it to a JSON format) and stores it in the metadata database (in the dag_code and serialized_dag tables). This is done to optimize reading of DAGs, as the database can be queried instead of reading the entire Python file each time.

## Scheduler checks if the DAG is ready to run based on the schedule:
- The scheduler checks if the DAG is due to run based on the schedule (cron, interval, or other triggers). It also checks other conditions like start_date, end_date, and any task dependencies.

## Scheduler creates a DAG Run and Task Instances:
- If a DAG is due to run, the scheduler creates a DAG Run (an instance of that DAG execution) and creates Task Instances for each task in the DAG.
- The state of each Task Instance (e.g., queued, running, success, failed, up_for_retry) is stored in the metadata database for tracking purposes.

## Scheduler assigns task instances to an Executor:
- The scheduler assigns tasks to an Executor based on the type of executor configured:
    - **LocalExecutor:** Executes tasks locally in parallel.
    - **CeleryExecutor:** Distributes tasks to multiple workers via a Celery queue.
    - **KubernetesExecutor:** Spins up Kubernetes pods to execute tasks.

## Executor pushes the task instance to the queue:
- The executor receives the task instance from the scheduler and pushes it to the execution queue. Depending on the executor type, this could be a local, Celery, or Kubernetes queue.

## Worker picks up the task instance from the queue and executes it:
- A Worker process (which could be local, a Celery worker, or a Kubernetes pod) picks up the task instance from the queue and starts executing the task.
- Workers are responsible for running the task code (e.g., Python scripts, SQL queries, etc.) defined in the task.

## Worker updates the task state in the metadata database:
- As the task runs, the worker reports task states (e.g., queued, running, success, failed, up_for_retry) back to the metadata database.
- After completing the task, the worker updates the task instance state in the database as either success or failed.

## Logging and monitoring:
- Throughout execution, logs are generated for each task. These logs can be stored locally or in remote storage (e.g., Amazon S3, Google Cloud Storage), depending on the configuration.
- Airflow’s UI allows you to monitor DAG runs and task instances, view logs, and retry or mark tasks as successful or failed.

## Retries and dependencies:
- If a task fails, the retry policy specified in the task’s configuration determines whether the task is retried and how many times.
- Task dependencies (like upstream tasks) are respected. Tasks only run once their dependencies are successfully completed, based on the depends_on_past, wait_for_downstream, or trigger_rule settings.

## Completion:
- Once all tasks in a DAG run are complete (either successfully or failed), the DAG run is marked as complete.

## Additional Notes:
- **Trigger DAGs manually:** In addition to schedules, DAGs can be manually triggered via the Airflow UI, CLI, or API.
- **Backfilling:** Airflow can backfill DAG runs for missed schedules (depending on the catchup configuration).
- **Sensors:** Airflow has sensors to wait for certain conditions to be met (e.g., the arrival of a file or completion of an external process) before proceeding with task execution.