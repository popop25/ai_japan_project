from __future__ import annotations

from .interfaces import PromptHandoffService
from .models import Task
from .renderers import render_critic_packet, render_pm_packet


class LocalPromptHandoffService(PromptHandoffService):
    def create_pm_packet(self, task: Task, context_markdown: str, skill_text: str) -> str:
        return render_pm_packet(task, context_markdown, skill_text)

    def create_critic_packet(
        self,
        task: Task,
        context_markdown: str,
        critic_skill_text: str,
        pm_output_markdown: str,
    ) -> str:
        return render_critic_packet(task, context_markdown, critic_skill_text, pm_output_markdown)
