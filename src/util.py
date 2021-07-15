from dataclasses import dataclass
from typing import List
import logging


@dataclass
class LogEntry:
    tag: str
    message: str
    level: int = logging.INFO


class IndicatorLogEntry:
    indicator_uuid: str
    indicator_group: int
    indicator_type: str
    indicator_value: str
    indicator_context_before: str
    indicator_context_after: str

    def __init__(self, indicator_uuid: str,
                 indicator_group: int,
                 indicator_type: str,
                 indicator_value: str,
                 indicator_context_before: str,
                 indicator_context_after: str):
        self.indicator_uuid = indicator_uuid
        self.indicator_group = indicator_group
        self.indicator_type = indicator_type
        self.indicator_value = indicator_value
        self.indicator_context_before = indicator_context_before
        self.indicator_context_after = indicator_context_after


class LogCollector:
    logs: List[LogEntry]
    indicator_logs: List[IndicatorLogEntry]

    def __init__(self):
        self.logs = []
        self.indicator_logs = []

    def add(self, tag: str, message: str, level: int = logging.INFO):
        self.logs.append(LogEntry(tag, message, level))

    def add_entry(self, log: LogEntry):
        self.logs.append(log)

    def __str__(self) -> str:
        result = ""
        for log in self.logs:
            result += f"[{logging.getLevelName(log.level)}] [{log.tag}] {log.message}\n"
        return result

    def render_logs(self):
        logs = []
        for log in self.logs:
            logs.append(f"[{logging.getLevelName(log.level)}] [{log.tag}] {log.message}")
        return logs

    # def create_logs_for_indicators(self, indicator_groups: List):
    #     for i in range(len(indicator_groups)):
    #         self.add('Indicator Extraction', f'Indicators in Group {i}', logging.INFO)
    #         for indicator in indicator_groups[i].indicators:
    #             context = indicator.paragraph.get_text()
    #             before = context[:indicator.start_index]
    #             after = context[indicator.start_index + len(indicator.value):]
    #             highlighted_context = f'{before}<b>{indicator.value}</b>{after}'
    #             self.add('Indicator Extraction',
    #                      f'[{type(indicator).__name__}] value="{indicator.value}, context="{highlighted_context}"',
    #                      logging.INFO)

    def create_logs_for_indicators(self, indicator_groups: List):
        for i in range(len(indicator_groups)):
            for indicator in indicator_groups[i]:
                context = indicator.paragraph.get_text()
                # Include paragraphs before + after if the context does not contain much more information than the indicator itself
                if (len(context) <= len(indicator.value)*1.2):
                    section = indicator.paragraph.parent
                    paragraph_before = None
                    paragraph_after = None
                    paragraph_found = False
                    for paragraph in section:
                        if paragraph_found:
                            paragraph_after = paragraph
                            break
                        if paragraph == indicator.paragraph:
                            paragraph_found = True
                        else:
                            paragraph_before = paragraph
                    if paragraph_before is not None:
                        context = paragraph_before.get_text() + context
                    if paragraph_after is not None:
                        context += paragraph_after.get_text()
                before = context[:indicator.start_index]
                after = context[indicator.start_index + len(indicator.value):]
                # highlighted_context = f'{before}<b>{indicator.value}</b>{after}'
                log_entry = IndicatorLogEntry(indicator_uuid=indicator.uuid,
                                              indicator_group=i,
                                              indicator_type=indicator.get_visual_name(),
                                              indicator_value=indicator.value,
                                              indicator_context_before=before,
                                              indicator_context_after=after)
                self.indicator_logs.append(log_entry)

    def get_indicator_logs_by_group(self):
        result = []
        if len(self.indicator_logs) > 0:
            max_indicator_group = max([i.indicator_group for i in self.indicator_logs])
            result = [None] * (max_indicator_group + 1)
            for i in self.indicator_logs:
                if result[i.indicator_group] is None:
                    result[i.indicator_group] = [[i.indicator_type, i.indicator_value, i.indicator_context_before, i.indicator_context_after, i.indicator_uuid]]
                else:
                    result[i.indicator_group].append([i.indicator_type, i.indicator_value, i.indicator_context_before, i.indicator_context_after, i.indicator_uuid])
        return result

    def get_info_logs(self):
        info_logs = [l for l in self.logs if l.level == logging.INFO]
        result = []
        for l in info_logs:
            result.append([l.tag, l.message])
        return result
