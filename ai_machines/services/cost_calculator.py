"""
Cost Calculator Service
Calculates estimated costs for assets, shots, and sequences based on complexity and type.
"""

from decimal import Decimal

# Cost multipliers based on complexity
COMPLEXITY_MULTIPLIERS = {
    'low': Decimal('1.0'),
    'medium': Decimal('2.0'),
    'high': Decimal('4.0'),
}

# Base costs by asset type (in USD)
ASSET_BASE_COSTS = {
    'model': Decimal('500'),
    'prop': Decimal('100'),
    'environment': Decimal('2000'),
    'effect': Decimal('1500'),
}

# Shot costs per day (in USD)
SHOT_DAILY_COSTS = {
    'low': Decimal('500'),
    'medium': Decimal('1500'),
    'high': Decimal('4000'),
}

# Base labor cost per hour
LABOR_COST_PER_HOUR = Decimal('100.00')


def parse_time_to_days(time_string):
    """
    Parse time string to days.
    Examples:
    - "1-2 days" -> 1.5
    - "3 days" -> 3
    - "1 week" -> 7
    - "2 weeks" -> 14
    """
    if not time_string:
        return Decimal('1.0')
    
    time_string = time_string.lower().strip()
    
    # Handle ranges like "1-2 days"
    if '-' in time_string:
        parts = time_string.split('-')
        if len(parts) == 2:
            try:
                start = float(parts[0].strip().split()[0])
                end = float(parts[1].strip().split()[0])
                avg = (start + end) / 2
                return Decimal(str(avg))
            except (ValueError, IndexError):
                pass
    
    # Handle single numbers
    try:
        # Extract number
        import re
        numbers = re.findall(r'\d+\.?\d*', time_string)
        if numbers:
            days = float(numbers[0])
            
            # Check for weeks
            if 'week' in time_string:
                days *= 7
            elif 'month' in time_string:
                days *= 30
            elif 'hour' in time_string:
                days /= 24
            
            return Decimal(str(days))
    except (ValueError, TypeError):
        pass
    
    # Default to 1 day if parsing fails
    return Decimal('1.0')


def calculate_asset_cost(asset):
    """
    Calculate estimated cost for an asset based on type and complexity.
    
    Args:
        asset: StoryAsset instance or dict with 'asset_type' and 'complexity'
    
    Returns:
        Decimal: Estimated cost in USD
    """
    if isinstance(asset, dict):
        asset_type = asset.get('asset_type', 'model')
        complexity = asset.get('complexity', 'medium')
    else:
        asset_type = asset.asset_type
        complexity = asset.complexity
    
    base_cost = ASSET_BASE_COSTS.get(asset_type.lower(), ASSET_BASE_COSTS['model'])
    multiplier = COMPLEXITY_MULTIPLIERS.get(complexity.lower(), COMPLEXITY_MULTIPLIERS['medium'])
    
    return base_cost * multiplier


def calculate_shot_cost(shot):
    """
    Calculate estimated cost for a shot based on complexity and estimated time.
    
    Args:
        shot: Shot instance or dict with 'complexity' and 'estimated_time'
    
    Returns:
        Decimal: Estimated cost in USD
    """
    if isinstance(shot, dict):
        complexity = shot.get('complexity', 'medium')
        estimated_time = shot.get('estimated_time', '1 day')
    else:
        complexity = shot.complexity
        estimated_time = shot.estimated_time or '1 day'
    
    days = parse_time_to_days(estimated_time)
    daily_cost = SHOT_DAILY_COSTS.get(complexity.lower(), SHOT_DAILY_COSTS['medium'])
    
    return days * daily_cost


def calculate_sequence_cost(sequence):
    """
    Calculate estimated cost for a sequence by summing up all shot costs.
    
    Args:
        sequence: Sequence instance with related shots
    
    Returns:
        Decimal: Total estimated cost for the sequence
    """
    total_cost = Decimal('0.0')
    
    if hasattr(sequence, 'shots'):
        for shot in sequence.shots.all():
            shot_cost = calculate_shot_cost(shot)
            total_cost += shot_cost
    
    return total_cost


def calculate_story_total_cost(story):
    """
    Calculate total estimated cost for a story.
    Sums up costs from all assets and shots.
    
    Args:
        story: Story instance
    
    Returns:
        Decimal: Total estimated cost in USD
    """
    total_cost = Decimal('0.0')
    
    # Calculate asset costs
    if hasattr(story, 'story_assets'):
        for asset in story.story_assets.all():
            asset_cost = calculate_asset_cost(asset)
            total_cost += asset_cost
    
    # Calculate shot costs
    if hasattr(story, 'shots'):
        for shot in story.shots.all():
            shot_cost = calculate_shot_cost(shot)
            total_cost += shot_cost
    
    return total_cost


def get_budget_range(total_cost):
    """
    Convert total cost to budget range string.
    
    Args:
        total_cost: Decimal total cost
    
    Returns:
        str: Budget range like "$50k-$100k"
    """
    if not total_cost or total_cost == 0:
        return ""
    
    cost_float = float(total_cost)
    
    if cost_float < 1000:
        return f"${cost_float:,.0f}"
    elif cost_float < 10000:
        return f"${cost_float/1000:.1f}k"
    elif cost_float < 100000:
        # Round to nearest 10k
        lower = int(cost_float / 10000) * 10
        upper = lower + 10
        return f"${lower}k-${upper}k"
    elif cost_float < 1000000:
        # Round to nearest 50k
        lower = int(cost_float / 50000) * 50
        upper = lower + 50
        return f"${lower}k-${upper}k"
    else:
        # Round to nearest 100k
        lower = int(cost_float / 100000) * 100
        upper = lower + 100
        return f"${lower}k-${upper}k"

