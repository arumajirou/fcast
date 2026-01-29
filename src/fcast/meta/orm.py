from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, Float, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON

Base = declarative_base()

def _uuid():
    return str(uuid.uuid4())

JSON = SQLITE_JSON  # sqlite-friendly; postgres can map via dialect if needed

# -----------------------
# registry
# -----------------------
class RegistryLibrary(Base):
    __tablename__ = "registry_library"
    library_id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String, nullable=False, unique=True)
    vendor = Column(String)
    repo_url = Column(Text)
    docs_url = Column(Text)
    license = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    releases = relationship("RegistryRelease", back_populates="library")

class RegistryRelease(Base):
    __tablename__ = "registry_release"
    release_id = Column(String(36), primary_key=True, default=_uuid)
    library_id = Column(String(36), ForeignKey("registry_library.library_id"), nullable=False)
    version = Column(String, nullable=False)
    commit_sha = Column(String)
    released_at = Column(DateTime)
    captured_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    facets = Column(JSON, nullable=False, default=dict)

    library = relationship("RegistryLibrary", back_populates="releases")
    symbols = relationship("RegistrySymbol", back_populates="release")

    __table_args__ = (
        UniqueConstraint("library_id", "version", "commit_sha", name="uq_release_version_sha"),
        Index("ix_release_library", "library_id"),
    )

class RegistrySymbol(Base):
    __tablename__ = "registry_symbol"
    symbol_id = Column(String(36), primary_key=True, default=_uuid)
    release_id = Column(String(36), ForeignKey("registry_release.release_id"), nullable=False)
    kind = Column(String, nullable=False)  # class/function/method/endpoint
    qualname = Column(Text, nullable=False)
    parent_symbol_id = Column(String(36), ForeignKey("registry_symbol.symbol_id"))
    doc_url = Column(Text)
    source_url = Column(Text)
    deprecated = Column(Boolean, nullable=False, default=False)
    facets = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    release = relationship("RegistryRelease", back_populates="symbols")
    parent = relationship("RegistrySymbol", remote_side=[symbol_id])

    signatures = relationship("RegistrySignature", back_populates="symbol")

    __table_args__ = (
        UniqueConstraint("release_id", "qualname", name="uq_symbol_release_qualname"),
        Index("ix_symbol_release", "release_id"),
        Index("ix_symbol_parent", "parent_symbol_id"),
    )

class RegistrySignature(Base):
    __tablename__ = "registry_signature"
    signature_id = Column(String(36), primary_key=True, default=_uuid)
    symbol_id = Column(String(36), ForeignKey("registry_symbol.symbol_id"), nullable=False)
    signature_text = Column(Text, nullable=False)
    return_type_repr = Column(Text)
    source = Column(String, nullable=False)  # docs/introspection/manual
    extracted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    symbol = relationship("RegistrySymbol", back_populates="signatures")
    params = relationship("RegistryParam", back_populates="signature")

    __table_args__ = (Index("ix_sig_symbol", "symbol_id"),)

class RegistryParam(Base):
    __tablename__ = "registry_param"
    param_id = Column(String(36), primary_key=True, default=_uuid)
    signature_id = Column(String(36), ForeignKey("registry_signature.signature_id"), nullable=False)
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    kind = Column(String, nullable=False)  # positional/keyword/varargs/varkw
    required = Column(Boolean, nullable=False)
    type_repr = Column(Text)
    default_repr = Column(Text)
    doc_text = Column(Text)
    facets = Column(JSON, nullable=False, default=dict)

    signature = relationship("RegistrySignature", back_populates="params")
    enums = relationship("RegistryParamEnum", back_populates="param")
    constraints = relationship("RegistryParamConstraint", back_populates="param")

    __table_args__ = (
        UniqueConstraint("signature_id", "name", name="uq_param_sig_name"),
        Index("ix_param_name", "name"),
    )

class RegistryParamEnum(Base):
    __tablename__ = "registry_param_enum"
    param_enum_id = Column(String(36), primary_key=True, default=_uuid)
    param_id = Column(String(36), ForeignKey("registry_param.param_id"), nullable=False)
    value_repr = Column(Text, nullable=False)
    label = Column(Text)
    is_deprecated = Column(Boolean, nullable=False, default=False)

    param = relationship("RegistryParam", back_populates="enums")

    __table_args__ = (
        UniqueConstraint("param_id", "value_repr", name="uq_param_enum"),
        Index("ix_enum_param", "param_id"),
    )

class RegistryParamConstraint(Base):
    __tablename__ = "registry_param_constraint"
    constraint_id = Column(String(36), primary_key=True, default=_uuid)
    param_id = Column(String(36), ForeignKey("registry_param.param_id"), nullable=False)
    constraint_type = Column(String, nullable=False)
    constraint_json = Column(JSON, nullable=False, default=dict)
    error_message = Column(Text)
    severity = Column(String, nullable=False, default="error")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    param = relationship("RegistryParam", back_populates="constraints")

    __table_args__ = (Index("ix_constraint_param", "param_id"),)

class RegistryCapability(Base):
    __tablename__ = "registry_capability"
    capability_id = Column(String(36), primary_key=True, default=_uuid)
    code = Column(String, nullable=False, unique=True)
    description = Column(Text)

class RegistrySymbolCapability(Base):
    __tablename__ = "registry_symbol_capability"
    symbol_capability_id = Column(String(36), primary_key=True, default=_uuid)
    symbol_id = Column(String(36), ForeignKey("registry_symbol.symbol_id"), nullable=False)
    capability_id = Column(String(36), ForeignKey("registry_capability.capability_id"), nullable=False)
    value_json = Column(JSON, nullable=False, default=dict)
    source = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_symcap_symbol", "symbol_id"),
        Index("ix_symcap_cap", "capability_id"),
        UniqueConstraint("symbol_id", "capability_id", name="uq_symcap"),
    )

class RegistryLoss(Base):
    __tablename__ = "registry_loss"
    loss_id = Column(String(36), primary_key=True, default=_uuid)
    library_id = Column(String(36), ForeignKey("registry_library.library_id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # point/probabilistic
    output_type = Column(String, nullable=False)  # point/quantile/distribution
    doc_text = Column(Text)

    __table_args__ = (UniqueConstraint("library_id", "name", name="uq_loss_lib_name"),)

class RegistryModelLossCompat(Base):
    __tablename__ = "registry_model_loss_compat"
    compat_id = Column(String(36), primary_key=True, default=_uuid)
    symbol_id = Column(String(36), ForeignKey("registry_symbol.symbol_id"), nullable=False)
    loss_id = Column(String(36), ForeignKey("registry_loss.loss_id"), nullable=False)
    support_level = Column(String, nullable=False)  # spec_ok/tested_ok/unsupported
    notes = Column(Text)
    last_tested_run_id = Column(String(36))

    __table_args__ = (UniqueConstraint("symbol_id", "loss_id", name="uq_model_loss"),)

class RegistryProviderEndpoint(Base):
    __tablename__ = "registry_provider_endpoint"
    endpoint_id = Column(String(36), primary_key=True, default=_uuid)
    library_id = Column(String(36), ForeignKey("registry_library.library_id"), nullable=False)
    name = Column(String, nullable=False)
    endpoint_type = Column(String, nullable=False)  # local/remote
    endpoint_uri = Column(Text)
    auth_type = Column(String)
    io_schema = Column(JSON, nullable=False, default=dict)
    capabilities = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("library_id", "name", name="uq_endpoint"),)

class RegistrySearchDoc(Base):
    __tablename__ = "registry_search_doc"
    doc_id = Column(String(36), primary_key=True, default=_uuid)
    release_id = Column(String(36), ForeignKey("registry_release.release_id"), nullable=False)
    symbol_id = Column(String(36), ForeignKey("registry_symbol.symbol_id"))
    doc_text = Column(Text, nullable=False)
    tags = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (Index("ix_search_release", "release_id"),)

# -----------------------
# datasets (game-aware)
# -----------------------
class DatasetsGame(Base):
    __tablename__ = "datasets_game"
    game_id = Column(String(36), primary_key=True, default=_uuid)
    game_code = Column(String, nullable=False, unique=True)  # numbers3, loto6...
    active_from = Column(DateTime)
    active_to = Column(DateTime)
    rules_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class DatasetsGameSlot(Base):
    __tablename__ = "datasets_game_slot"
    game_slot_id = Column(String(36), primary_key=True, default=_uuid)
    game_id = Column(String(36), ForeignKey("datasets_game.game_id"), nullable=False)
    slot_code = Column(String, nullable=False)  # N1...
    slot_index = Column(Integer, nullable=False)
    slot_role = Column(String, nullable=False, default="main")
    slot_meta = Column(JSON, nullable=False, default=dict)

    __table_args__ = (UniqueConstraint("game_id", "slot_code", name="uq_game_slot"),)

class DatasetsDataset(Base):
    __tablename__ = "datasets_dataset"
    dataset_id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String, nullable=False, unique=True)  # e.g., loto6_jp
    game_id = Column(String(36), ForeignKey("datasets_game.game_id"), nullable=False)
    domain = Column(String)
    timezone = Column(String, nullable=False, default="Asia/Tokyo")
    owner = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class DatasetsVersion(Base):
    __tablename__ = "datasets_version"
    dataset_version_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets_dataset.dataset_id"), nullable=False)
    source_snapshot = Column(JSON, nullable=False, default=dict)
    row_count = Column(Integer)
    schema_hash = Column(String)
    lake_uri = Column(Text, nullable=False)
    facets = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (Index("ix_dsv_dataset", "dataset_id"),)

class DatasetsSeries(Base):
    __tablename__ = "datasets_series"
    series_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets_dataset.dataset_id"), nullable=False)
    unique_id = Column(String, nullable=False)  # N1..Nk
    slot_index = Column(Integer, nullable=False)
    label = Column(String)

    __table_args__ = (UniqueConstraint("dataset_id", "unique_id", name="uq_dataset_uid"),)

class DatasetsArtifact(Base):
    __tablename__ = "datasets_artifact"
    artifact_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_version_id = Column(String(36), ForeignKey("datasets_version.dataset_version_id"), nullable=False)
    layer = Column(String, nullable=False)  # bronze/silver/gold
    table_name = Column(String, nullable=False)
    storage_uri = Column(Text, nullable=False)
    schema_hash = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# -----------------------
# features
# -----------------------
class FeaturesGenerator(Base):
    __tablename__ = "features_generator"
    generator_id = Column(String(36), primary_key=True, default=_uuid)
    kind = Column(String, nullable=False)  # ts_feature_lib/foundation_embed/unsupervised/custom
    provider_ref = Column(JSON, nullable=False, default=dict)  # {library, release, symbol or endpoint}
    params_json = Column(JSON, nullable=False, default=dict)
    output_schema_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class FeaturesDef(Base):
    __tablename__ = "features_def"
    feature_id = Column(String(36), primary_key=True, default=_uuid)
    generator_id = Column(String(36), ForeignKey("features_generator.generator_id"))
    name = Column(String, nullable=False, unique=True)
    group = Column(String, nullable=False)  # hist/stat/fut
    dtype = Column(String, nullable=False)
    definition_json = Column(JSON, nullable=False, default=dict)
    owner = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class FeaturesSet(Base):
    __tablename__ = "features_set"
    feature_set_id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String, nullable=False, unique=True)
    purpose = Column(String, nullable=False)  # train/predict/anomaly/xai
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class FeaturesSetItem(Base):
    __tablename__ = "features_set_item"
    feature_set_item_id = Column(String(36), primary_key=True, default=_uuid)
    feature_set_id = Column(String(36), ForeignKey("features_set.feature_set_id"), nullable=False)
    feature_id = Column(String(36), ForeignKey("features_def.feature_id"), nullable=False)
    required = Column(Boolean, nullable=False, default=True)
    ord = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("feature_set_id", "feature_id", name="uq_featureset_feature"),
        Index("ix_featureset_ord", "feature_set_id", "ord"),
    )

class FeaturesMaterialization(Base):
    __tablename__ = "features_materialization"
    feat_mat_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_version_id = Column(String(36), ForeignKey("datasets_version.dataset_version_id"), nullable=False)
    feature_set_id = Column(String(36), ForeignKey("features_set.feature_set_id"), nullable=False)
    storage_uri = Column(Text, nullable=False)
    schema_hash = Column(String)
    facets = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("dataset_version_id", "feature_set_id", name="uq_mat_ds_fs"),)

class FeaturesAvailability(Base):
    __tablename__ = "features_availability"
    availability_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_version_id = Column(String(36), ForeignKey("datasets_version.dataset_version_id"), nullable=False)
    feature_id = Column(String(36), ForeignKey("features_def.feature_id"), nullable=False)
    available_from = Column(DateTime)
    available_to = Column(DateTime)
    covers_horizon = Column(Boolean, nullable=False)
    notes = Column(Text)

    __table_args__ = (UniqueConstraint("dataset_version_id", "feature_id", name="uq_feat_avail"),)

# -----------------------
# models
# -----------------------
class ModelsSeriesSelector(Base):
    __tablename__ = "models_series_selector"
    selector_id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String, nullable=False, unique=True)
    game_code = Column(String, nullable=False)  # e.g., loto6
    unique_id_list = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class ModelsRegistry(Base):
    __tablename__ = "models_registry"
    model_id = Column(String(36), primary_key=True, default=_uuid)
    release_id = Column(String(36), ForeignKey("registry_release.release_id"), nullable=False)
    model_symbol_id = Column(String(36), ForeignKey("registry_symbol.symbol_id"))
    endpoint_id = Column(String(36), ForeignKey("registry_provider_endpoint.endpoint_id"))
    train_dataset_version_id = Column(String(36), ForeignKey("datasets_version.dataset_version_id"), nullable=False)
    feature_set_id = Column(String(36), ForeignKey("features_set.feature_set_id"), nullable=False)
    selector_id = Column(String(36), ForeignKey("models_series_selector.selector_id"), nullable=False)
    series_mode = Column(String, nullable=False)  # multivariate_joint/global_univariate
    n_series = Column(Integer)
    artifact_uri = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)

    __table_args__ = (
        Index("ix_model_selector", "selector_id"),
        Index("ix_model_release", "release_id"),
    )

class ModelsExogSpec(Base):
    __tablename__ = "models_exog_spec"
    exog_spec_id = Column(String(36), primary_key=True, default=_uuid)
    model_id = Column(String(36), ForeignKey("models_registry.model_id"), nullable=False, unique=True)
    hist_cols = Column(JSON, nullable=False, default=list)
    stat_cols = Column(JSON, nullable=False, default=list)
    fut_cols = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class ModelsProperty(Base):
    __tablename__ = "models_property"
    prop_id = Column(String(36), primary_key=True, default=_uuid)
    model_id = Column(String(36), ForeignKey("models_registry.model_id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(JSON, nullable=False, default=dict)

    __table_args__ = (UniqueConstraint("model_id", "key", name="uq_model_prop"),)

class ModelsDependency(Base):
    __tablename__ = "models_dependency"
    dep_id = Column(String(36), primary_key=True, default=_uuid)
    model_id = Column(String(36), ForeignKey("models_registry.model_id"), nullable=False)
    depends_on_model_id = Column(String(36), ForeignKey("models_registry.model_id"), nullable=False)
    dep_type = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("model_id", "depends_on_model_id", "dep_type", name="uq_model_dep"),)

# -----------------------
# runs
# -----------------------
class RunsDatasetBinding(Base):
    __tablename__ = "runs_dataset_binding"
    binding_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_version_id = Column(String(36), ForeignKey("datasets_version.dataset_version_id"), nullable=False)
    df_engine = Column(String, nullable=False, default="pandas")
    id_col = Column(String, nullable=False, default="unique_id")
    time_col = Column(String, nullable=False, default="ds")
    target_col = Column(String, nullable=False, default="y")
    feature_table_uri = Column(Text)
    static_table_uri = Column(Text)
    futr_table_uri = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class RunsPlan(Base):
    __tablename__ = "runs_plan"
    run_id = Column(String(36), primary_key=True, default=_uuid)
    model_id = Column(String(36), ForeignKey("models_registry.model_id"), nullable=False)
    binding_id = Column(String(36), ForeignKey("runs_dataset_binding.binding_id"), nullable=False)
    plan_name = Column(String)
    pipeline_json = Column(JSON, nullable=False, default=dict)
    status = Column(String, nullable=False, default="created")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    facets = Column(JSON, nullable=False, default=dict)

class RunsStep(Base):
    __tablename__ = "runs_step"
    run_step_id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(36), ForeignKey("runs_plan.run_id"), nullable=False)
    step_name = Column(String, nullable=False)  # fit/predict/evaluate/save/load
    ord = Column(Integer, nullable=False)
    symbol_id = Column(String(36), ForeignKey("registry_symbol.symbol_id"))
    depends_on_step_id = Column(String(36), ForeignKey("runs_step.run_step_id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (Index("ix_step_run", "run_id"),)

class RunsParam(Base):
    __tablename__ = "runs_param"
    run_param_id = Column(String(36), primary_key=True, default=_uuid)
    run_step_id = Column(String(36), ForeignKey("runs_step.run_step_id"), nullable=False, unique=True)
    params = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class RunsValidation(Base):
    __tablename__ = "runs_validation"
    validation_id = Column(String(36), primary_key=True, default=_uuid)
    run_step_id = Column(String(36), ForeignKey("runs_step.run_step_id"), nullable=False, unique=True)
    ok = Column(Boolean, nullable=False)
    violations = Column(JSON, nullable=False, default=list)
    validated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class RunsResult(Base):
    __tablename__ = "runs_result"
    run_result_id = Column(String(36), primary_key=True, default=_uuid)
    run_step_id = Column(String(36), ForeignKey("runs_step.run_step_id"), nullable=False, unique=True)
    status = Column(String, nullable=False)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    summary = Column(JSON, nullable=False, default=dict)

class RunsMetric(Base):
    __tablename__ = "runs_metric"
    metric_id = Column(String(36), primary_key=True, default=_uuid)
    run_step_id = Column(String(36), ForeignKey("runs_step.run_step_id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    split_tag = Column(String)
    window_index = Column(Integer)
    meta = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (Index("ix_metric_step", "run_step_id"), Index("ix_metric_name", "metric_name"),)

class RunsError(Base):
    __tablename__ = "runs_error"
    error_id = Column(String(36), primary_key=True, default=_uuid)
    run_step_id = Column(String(36), ForeignKey("runs_step.run_step_id"), nullable=False)
    exception_type = Column(String)
    message = Column(Text)
    traceback = Column(Text)
    trace_hash = Column(String)
    input_snapshot = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class RunsArtifact(Base):
    __tablename__ = "runs_artifact"
    artifact_id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(36), ForeignKey("runs_plan.run_id"), nullable=False)
    artifact_type = Column(String, nullable=False)
    storage_uri = Column(Text, nullable=False)
    meta = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# -----------------------
# observe
# -----------------------
class ObserveJob(Base):
    __tablename__ = "observe_job"
    job_id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(36), ForeignKey("runs_plan.run_id"), nullable=False)
    job_type = Column(String, nullable=False)
    spark_app_id = Column(String)
    cluster_id = Column(String)
    status = Column(String)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    facets = Column(JSON, nullable=False, default=dict)

class ObserveResourceSummary(Base):
    __tablename__ = "observe_resource_summary"
    res_sum_id = Column(String(36), primary_key=True, default=_uuid)
    job_id = Column(String(36), ForeignKey("observe_job.job_id"), nullable=False, unique=True)
    cpu_time_sec = Column(Float)
    max_ram_mb = Column(Float)
    max_vram_mb = Column(Float)
    io_read_mb = Column(Float)
    io_write_mb = Column(Float)
    extra = Column(JSON, nullable=False, default=dict)

class ObserveResourceSample(Base):
    __tablename__ = "observe_resource_sample"
    res_sample_id = Column(String(36), primary_key=True, default=_uuid)
    job_id = Column(String(36), ForeignKey("observe_job.job_id"), nullable=False)
    ts = Column(DateTime, nullable=False, default=datetime.utcnow)
    cpu_pct = Column(Float)
    ram_mb = Column(Float)
    vram_mb = Column(Float)
    io_r_mb_s = Column(Float)
    io_w_mb_s = Column(Float)

    __table_args__ = (UniqueConstraint("job_id", "ts", name="uq_job_ts"),)

# -----------------------
# xai
# -----------------------
class XaiRun(Base):
    __tablename__ = "xai_run"
    xai_run_id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(36), ForeignKey("runs_plan.run_id"), nullable=False)
    method = Column(String, nullable=False)
    params = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class XaiFeatureImportance(Base):
    __tablename__ = "xai_feature_importance"
    xai_fi_id = Column(String(36), primary_key=True, default=_uuid)
    xai_run_id = Column(String(36), ForeignKey("xai_run.xai_run_id"), nullable=False)
    feature_name = Column(String, nullable=False)
    importance_mean_abs = Column(Float)
    importance_std = Column(Float)

    __table_args__ = (UniqueConstraint("xai_run_id", "feature_name", name="uq_xai_feature"),)

class XaiMaterialization(Base):
    __tablename__ = "xai_materialization"
    xai_mat_id = Column(String(36), primary_key=True, default=_uuid)
    xai_run_id = Column(String(36), ForeignKey("xai_run.xai_run_id"), nullable=False, unique=True)
    storage_uri = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# -----------------------
# govern
# -----------------------
class GovernDQIssue(Base):
    __tablename__ = "govern_dq_issue"
    dq_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_version_id = Column(String(36), ForeignKey("datasets_version.dataset_version_id"), nullable=False)
    unique_id = Column(String)
    ds = Column(Text)
    rule = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class GovernLeakCheck(Base):
    __tablename__ = "govern_leak_check"
    leak_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_version_id = Column(String(36), ForeignKey("datasets_version.dataset_version_id"), nullable=False)
    feature_id = Column(String(36), ForeignKey("features_def.feature_id"), nullable=False)
    suspicion_score = Column(Float)
    evidence = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class GovernSourcePolicy(Base):
    __tablename__ = "govern_source_policy"
    policy_id = Column(String(36), primary_key=True, default=_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets_dataset.dataset_id"), nullable=False)
    terms_uri = Column(Text)
    checked_at = Column(DateTime)
    notes = Column(Text)
