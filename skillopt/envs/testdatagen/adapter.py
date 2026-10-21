"""Adapter for Test Data Generator environment."""
from __future__ import annotations

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter
from skillopt.envs.testdatagen.dataloader import TestDataGenDataLoader
from skillopt.envs.testdatagen.rollout import run_batch


class TestDataGenAdapter(EnvAdapter):
    def __init__(
        self,
        split_dir: str = "",
        split_mode: str = "split_dir",
        split_ratio: str = "2:1:7",
        split_seed: int = 42,
        split_output_dir: str = "",
        workers: int = 4,
        analyst_workers: int = 8,
        failure_only: bool = False,
        minibatch_size: int = 4,
        edit_budget: int = 4,
        seed: int = 42,
        limit: int = 0,
    ) -> None:
        self.workers = workers
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.dataloader = TestDataGenDataLoader(
            split_dir=split_dir,
            split_mode=split_mode,
            split_ratio=split_ratio,
            split_seed=split_seed,
            split_output_dir=split_output_dir,
            seed=seed,
            limit=limit,
        )

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(batch_size=batch_size, seed=seed)
        return list(batch.payload or [])

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed)
        return list(batch.payload or [])

    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        return run_batch(
            items=env_manager,
            out_root=out_dir,
            skill_content=skill_content,
            workers=self.workers,
        )

    def get_task_types(self) -> list[str]:
        return ["testdatagen"]
