"""
ML 서비스 의존성 주입 컨테이너
ML 레지스트리 서비스들의 의존성 관리
"""

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_ml_session
from app.adapters.repositories.dataset_repository_impl import DatasetRepositoryImpl
from app.adapters.repositories.experiment_repository_impl import ExperimentRepositoryImpl
from app.application.use_cases.dataset_use_cases import (
    CreateDatasetUseCase,
    GetDatasetUseCase,
    GetDatasetByNameAndVersionUseCase,
    ListDatasetsUseCase,
    ListDatasetsByNameUseCase,
    ListDatasetsByTagUseCase,
    UpdateDatasetUseCase,
    DeleteDatasetUseCase
)
from app.application.use_cases.experiment_use_cases import (
    CreateExperimentUseCase,
    GetExperimentUseCase,
    GetExperimentByNameAndDatasetUseCase,
    ListExperimentsUseCase,
    ListExperimentsByDatasetUseCase,
    ListExperimentsByFrameworkUseCase,
    UpdateExperimentUseCase,
    DeleteExperimentUseCase,
    AddExperimentParamUseCase,
    AddExperimentMetricUseCase
)

class MLContainer(containers.DeclarativeContainer):
    """ML 서비스 의존성 주입 컨테이너"""
    
    # 데이터베이스 세션
    session = providers.Dependency(instance_of=AsyncSession)
    
    # 리포지토리
    dataset_repository = providers.Factory(
        DatasetRepositoryImpl,
        session=session
    )
    
    experiment_repository = providers.Factory(
        ExperimentRepositoryImpl,
        session=session
    )
    
    # 데이터셋 유즈케이스
    create_dataset_use_case = providers.Factory(
        CreateDatasetUseCase,
        dataset_repository=dataset_repository
    )
    
    get_dataset_use_case = providers.Factory(
        GetDatasetUseCase,
        dataset_repository=dataset_repository
    )
    
    get_dataset_by_name_and_version_use_case = providers.Factory(
        GetDatasetByNameAndVersionUseCase,
        dataset_repository=dataset_repository
    )
    
    list_datasets_use_case = providers.Factory(
        ListDatasetsUseCase,
        dataset_repository=dataset_repository
    )
    
    list_datasets_by_name_use_case = providers.Factory(
        ListDatasetsByNameUseCase,
        dataset_repository=dataset_repository
    )
    
    list_datasets_by_tag_use_case = providers.Factory(
        ListDatasetsByTagUseCase,
        dataset_repository=dataset_repository
    )
    
    update_dataset_use_case = providers.Factory(
        UpdateDatasetUseCase,
        dataset_repository=dataset_repository
    )
    
    delete_dataset_use_case = providers.Factory(
        DeleteDatasetUseCase,
        dataset_repository=dataset_repository
    )
    
    # 실험 유즈케이스
    create_experiment_use_case = providers.Factory(
        CreateExperimentUseCase,
        experiment_repository=experiment_repository
    )
    
    get_experiment_use_case = providers.Factory(
        GetExperimentUseCase,
        experiment_repository=experiment_repository
    )
    
    get_experiment_by_name_and_dataset_use_case = providers.Factory(
        GetExperimentByNameAndDatasetUseCase,
        experiment_repository=experiment_repository
    )
    
    list_experiments_use_case = providers.Factory(
        ListExperimentsUseCase,
        experiment_repository=experiment_repository
    )
    
    list_experiments_by_dataset_use_case = providers.Factory(
        ListExperimentsByDatasetUseCase,
        experiment_repository=experiment_repository
    )
    
    list_experiments_by_framework_use_case = providers.Factory(
        ListExperimentsByFrameworkUseCase,
        experiment_repository=experiment_repository
    )
    
    update_experiment_use_case = providers.Factory(
        UpdateExperimentUseCase,
        experiment_repository=experiment_repository
    )
    
    delete_experiment_use_case = providers.Factory(
        DeleteExperimentUseCase,
        experiment_repository=experiment_repository
    )
    
    add_experiment_param_use_case = providers.Factory(
        AddExperimentParamUseCase,
        experiment_repository=experiment_repository
    )
    
    add_experiment_metric_use_case = providers.Factory(
        AddExperimentMetricUseCase,
        experiment_repository=experiment_repository
    )

# 전역 컨테이너 인스턴스
ml_container = MLContainer()
