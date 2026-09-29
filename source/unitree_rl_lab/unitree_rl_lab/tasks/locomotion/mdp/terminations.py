from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import torch

from isaaclab.managers import ManagerTermBase, ManagerTermBaseCfg, SceneEntityCfg
from isaaclab.sensors import ContactSensor

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

#如果指定的機器人 body 接觸力超過 threshold，而且累積達到指定次數，就把該 env 判定為要 reset
class illegal_reset_contact(ManagerTermBase):
    def __init__(self, cfg: ManagerTermBaseCfg, env: ManagerBasedRLEnv):
        super().__init__(cfg, env)

        self.threshold = cfg.params["threshold"]
        self.sensor_cfg = cfg.params["sensor_cfg"]
        self.print_reason = cfg.params.get("print_reason", False)
        self.episode_length_threshold = cfg.params.get(
            "episode_length_threshold", 1
        )

        self.illegal_contact_counter = torch.zeros(
            env.num_envs,
            device=env.device,
            dtype=torch.int,
        )

    def __call__(
        self,
        env: ManagerBasedRLEnv,
        threshold: float,
        sensor_cfg: SceneEntityCfg,
        print_reason: bool = False,
        episode_length_threshold: int = 1,
    ) -> torch.Tensor:
        contact_sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
        net_contact_forces = contact_sensor.data.net_forces_w_history

        contacts = torch.any(
            torch.max(
                torch.norm(
                    net_contact_forces[:, :, sensor_cfg.body_ids],
                    dim=-1,
                ),
                dim=1,
            )[0]
            > threshold,
            dim=1,
        )

        self.illegal_contact_counter += contacts.int()

        # If contact count and episode length exceed the first
        # episode_length_threshold steps, trigger termination.
        reset_envs = torch.logical_and(
            self.illegal_contact_counter >= episode_length_threshold,
            env.episode_length_buf >= episode_length_threshold,
        )

        if reset_envs.any() and print_reason:
            print(f"illegal_reset_contact: {reset_envs.sum()} envs")

        return reset_envs

    def reset(self, env_ids: Sequence[int] | slice | None = None) -> None:
        if env_ids is None:
            env_ids = slice(None)

        self.illegal_contact_counter[env_ids] = 0