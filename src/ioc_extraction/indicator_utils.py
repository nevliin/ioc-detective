import enum
import logging
from functools import cmp_to_key
from typing import List, Dict

import yaml

from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.indicators.indicator_group import IndicatorGroup
from src.util import LogCollector


class IndicatorCombinationMode(enum.Enum):
    SECTION = 1
    DISTANCE_PARAGRAPHS = 2
    DISTANCE_CHARACTERS = 3


def combine_indicators(indicators_by_section: List[List[Indicator]], mode: IndicatorCombinationMode) -> List[
    IndicatorGroup]:
    if mode == IndicatorCombinationMode.SECTION:
        return combine_indicators_by_section(indicators_by_section)
    else:
        return combine_indicators_by_distance(indicators_by_section, mode)


def combine_indicators_by_distance(indicators_by_section: List[List[Indicator]], mode: IndicatorCombinationMode):
    indicators = [indicator for section in indicators_by_section for indicator in section]

    claims = lay_claims(indicators, mode)

    index_groups = evaluate_claims(claims, indicators)

    indicator_groups = []
    for index_group in index_groups:
        indicator_groups.append(IndicatorGroup([indicators[index] for index in index_group]))

    remaining_indicators = remove_claimed(index_groups, indicators)
    for indicator in remaining_indicators:
        indicator_groups.append(IndicatorGroup([indicator]))

    return indicator_groups


def lay_claims(indicators: List[Indicator], mode: IndicatorCombinationMode):
    claims = {}
    for j in range(len(indicators)):
        indicator = indicators[j]
        if len(indicator.secondary_indicator_types) > 0:
            section = indicator.paragraph.parent
            indicator_paragraph_index = section.get_index_of(indicator.paragraph)
            for i in range(len(indicators)):
                curr_indicator = indicators[i]
                # Check if the indicator is on the list of secondary indicators
                if type(curr_indicator) in indicator.secondary_indicator_types:
                    # Check if the indicators are in the same section
                    if section == curr_indicator.paragraph.parent:
                        # Calculate paragraph distance
                        if mode == IndicatorCombinationMode.DISTANCE_PARAGRAPHS:
                            curr_indicator_paragraph_index = section.get_index_of(curr_indicator.paragraph)
                            # Check if the distance between the indicators is within the max distance
                            if abs(
                                    curr_indicator_paragraph_index - indicator_paragraph_index) <= indicator.secondary_indicators_max_distance:
                                if i not in claims:
                                    claims[i] = []
                                claims[i].append({
                                    'indicator_index': j,
                                    'distance': curr_indicator_paragraph_index - indicator_paragraph_index
                                })
                        # Calculate character distance
                        elif mode == IndicatorCombinationMode.DISTANCE_CHARACTERS:
                            distance = abs(curr_indicator.paragraph.global_position + curr_indicator.start_index) - (
                                    indicator.paragraph.global_position + indicator.start_index)
                            if i not in claims:
                                claims[i] = []
                            claims[i].append({
                                'indicator_index': j,
                                'distance': distance
                            })
    return claims


def evaluate_claims(claims: Dict[int, List[Dict]], indicators: List[Indicator]):
    index_groups = {}

    for key, value in claims.items():
        def comp_claims(a, b):
            # compare absolute distance
            if abs(a['distance']) > abs(b['distance']):
                return 1
            elif abs(a['distance']) == abs(b['distance']):
                # give preference to negative distances
                if a['distance'] > b['distance']:
                    return -1
                else:
                    return 1
            else:
                return -1

        value.sort(key=cmp_to_key(comp_claims))
        winning_claim_index = value[0]['indicator_index']
        if winning_claim_index not in index_groups:
            index_groups[winning_claim_index] = []
        index_groups[winning_claim_index].append(key)

    return [[key, *value] for key, value in index_groups.items()]


def remove_claimed(index_groups: List[List[int]], indicators: List) -> List[Indicator]:
    indices = sorted([item for sublist in index_groups for item in sublist])
    for i in reversed(indices):
        del indicators[i]

    return indicators


def combine_indicators_by_section(indicators_by_section: List[List[Indicator]]) -> List[IndicatorGroup]:
    indicator_groups = []

    for section in indicators_by_section:
        if len(section) > 0:
            group = IndicatorGroup(section)
            indicator_groups.append(group)

    return indicator_groups


def filter_indicator_groups(indicator_groups: List[IndicatorGroup], log_collector: LogCollector):
    non_standalone_indices = find_non_standalone_indicators(indicator_groups)
    for i in sorted(non_standalone_indices, reverse=True):
        log_collector.add('IoC Extraction', f'Removing indicator group {i} for being non-standalone',
                          level=logging.DEBUG)
        del indicator_groups[i]

    for group in indicator_groups:
        duplicate_indices = find_duplicated_indicators(group)
        for i in sorted(duplicate_indices, reverse=True):
            log_collector.add('IoC Extraction',
                              f'Removing indicator (type={group.indicators[i].__class__.__name__}, value={group.indicators[i].value}) for being duplicated',
                              level=logging.DEBUG)
            del group.indicators[i]

    return indicator_groups


def find_non_standalone_indicators(indicator_groups: List[IndicatorGroup]) -> List[int]:
    indices = []
    # Find indicator groups consisting of only non-standalone indicators
    for i in range(len(indicator_groups)):
        standalone = False
        indicator_type = None
        for indicator in indicator_groups[i]:
            if indicator_type is None:
                indicator_type = type(indicator).__name__
            if type(indicator).__name__ != indicator_type or indicator.standalone:
                standalone = True
                break

        if not standalone:
            indices.append(i)

    return indices


def find_duplicated_indicators(indicator_group: IndicatorGroup) -> List[int]:
    indices = []
    unique_indicators = set()
    for i in range(len(indicator_group.indicators)):
        value = (indicator_group.indicators[i].__class__.__name__, indicator_group.indicators[i].value)
        if value in unique_indicators:
            indices.append(i)
        else:
            unique_indicators.add(value)

    return indices
