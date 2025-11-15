"""
Analysis module for narrative generation.
Routes to either Claude AI or local rule-based narratives based on mode.
"""

from typing import Dict, Optional, Tuple, List
import requests
from bs4 import BeautifulSoup
import re
from anthropic import Anthropic
from modules.config import ANTHROPIC_API_KEY
from modules.narratives import build_context_prompt, save_narrative
from modules.local_narrative import build_local_narrative


def fetch_claude_pricing_from_web() -> Dict[str, Dict[str, float]]:
    """
    Scrape latest Claude pricing data from Anthropic's website.
    Falls back to cached values if scraping fails.
    
    Returns:
        Dictionary mapping model IDs to pricing info
    """
    # Fallback pricing data (current as of Nov 2024)
    fallback_costs = {
        'claude-3-5-haiku-20241022': {'input_cost': 1.0, 'output_cost': 5.0},
        'claude-3-5-sonnet-20241022': {'input_cost': 3.0, 'output_cost': 15.0},
        'claude-sonnet-4-20250514': {'input_cost': 3.0, 'output_cost': 15.0},
        'claude-opus-4-20250514': {'input_cost': 15.0, 'output_cost': 75.0}
    }
    
    try:
        # Fetch Anthropic pricing page
        response = requests.get('https://www.anthropic.com/pricing', timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract pricing data
        pricing_data = {}
        
        # Look for pricing patterns in the page
        # Typical format: "$X per million tokens" or "$X / MTok"
        text_content = soup.get_text()
        
        # Extract Haiku pricing
        haiku_match = re.search(r'Haiku.*?\$(\d+\.?\d*)\s*(?:per million|MTok|/\s*MTok).*?input.*?\$(\d+\.?\d*)\s*(?:per million|MTok|/\s*MTok).*?output', 
                               text_content, re.IGNORECASE | re.DOTALL)
        if haiku_match:
            pricing_data['claude-3-5-haiku-20241022'] = {
                'input_cost': float(haiku_match.group(1)),
                'output_cost': float(haiku_match.group(2))
            }
        
        # Extract Sonnet pricing
        sonnet_match = re.search(r'Sonnet.*?\$(\d+\.?\d*)\s*(?:per million|MTok|/\s*MTok).*?input.*?\$(\d+\.?\d*)\s*(?:per million|MTok|/\s*MTok).*?output', 
                                text_content, re.IGNORECASE | re.DOTALL)
        if sonnet_match:
            input_cost = float(sonnet_match.group(1))
            output_cost = float(sonnet_match.group(2))
            pricing_data['claude-3-5-sonnet-20241022'] = {
                'input_cost': input_cost,
                'output_cost': output_cost
            }
            pricing_data['claude-sonnet-4-20250514'] = {
                'input_cost': input_cost,
                'output_cost': output_cost
            }
        
        # Extract Opus pricing
        opus_match = re.search(r'Opus.*?\$(\d+\.?\d*)\s*(?:per million|MTok|/\s*MTok).*?input.*?\$(\d+\.?\d*)\s*(?:per million|MTok|/\s*MTok).*?output', 
                              text_content, re.IGNORECASE | re.DOTALL)
        if opus_match:
            pricing_data['claude-opus-4-20250514'] = {
                'input_cost': float(opus_match.group(1)),
                'output_cost': float(opus_match.group(2))
            }
        
        # If we successfully extracted any pricing, use it
        if pricing_data:
            # Merge with fallback for any missing models
            return {**fallback_costs, **pricing_data}
    
    except Exception as e:
        # If scraping fails, use fallback
        print(f"⚠️ Could not fetch live pricing from Anthropic website: {e}")
        print("📦 Using cached pricing data")
    
    return fallback_costs


def get_available_claude_models() -> List[Dict[str, str]]:
    """
    Fetch available Claude models from Anthropic API and enrich with live cost data.
    Scrapes pricing from Anthropic website, falls back to cached values if needed.
    Models are ordered by cost (cheapest to most expensive).
    
    Returns:
        List of dicts with keys: id, name, description, use_case, cost_detail, cost_comparison
    """
    # Fetch live pricing data from Anthropic website
    pricing_data = fetch_claude_pricing_from_web()
    
    # Model metadata (descriptions and use cases)
    model_metadata = {
        'claude-3-5-haiku-20241022': {
            'description': 'Fastest and most affordable',
            'use_case': '⚡ Budget-friendly option for quick daily check-ins'
        },
        'claude-3-5-sonnet-20241022': {
            'description': 'Previous generation, still very capable',
            'use_case': '💼 Solid choice for detailed narratives'
        },
        'claude-sonnet-4-20250514': {
            'description': 'Best balance of intelligence and speed',
            'use_case': '✨ Recommended for most users - excellent quality, fast responses'
        },
        'claude-opus-4-20250514': {
            'description': 'Highest intelligence and capability',
            'use_case': '🎯 Best for complex analysis requiring deep insights'
        }
    }
    
    # Merge pricing with metadata
    model_costs = {}
    for model_id, pricing in pricing_data.items():
        if model_id in model_metadata:
            model_costs[model_id] = {
                **pricing,
                **model_metadata[model_id]
            }
    
    # Try to fetch live models from Anthropic API
    available_models = []
    
    try:
        if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != 'your_key_here':
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            # Fetch models list
            models_response = client.models.list()
            
            # Process each model
            for model in models_response.data:
                model_id = model.id
                
                # Only include Claude models with known pricing
                if model_id in model_costs:
                    cost_info = model_costs[model_id]
                    
                    # Calculate cost comparison to cheapest (Haiku)
                    base_input = 1.0
                    base_output = 5.0
                    cost_multiplier_input = cost_info['input_cost'] / base_input
                    cost_multiplier_output = cost_info['output_cost'] / base_output
                    
                    if cost_multiplier_input == 1.0:
                        cost_comparison = 'Baseline (cheapest)'
                    else:
                        avg_multiplier = (cost_multiplier_input + cost_multiplier_output) / 2
                        percent_increase = int((avg_multiplier - 1) * 100)
                        cost_comparison = f'+{percent_increase}% cost vs Haiku ({int(cost_multiplier_input)}x input, {int(cost_multiplier_output)}x output)'
                    
                    available_models.append({
                        'id': model_id,
                        'name': model.display_name if hasattr(model, 'display_name') else model_id.replace('-', ' ').title(),
                        'description': cost_info['description'],
                        'use_case': cost_info['use_case'],
                        'cost_detail': f"${int(cost_info['input_cost'])} in / ${int(cost_info['output_cost'])} out per million tokens",
                        'cost_comparison': cost_comparison,
                        'input_cost': cost_info['input_cost'],
                        'output_cost': cost_info['output_cost']
                    })
            
            # Sort by cost (input_cost + output_cost)
            available_models.sort(key=lambda x: x['input_cost'] + x['output_cost'])
            
    except Exception as e:
        # If API fetch fails, return fallback list
        pass
    
    # Fallback to hardcoded list if API fetch failed or no API key
    if not available_models:
        for model_id, cost_info in model_costs.items():
            base_input = 1.0
            base_output = 5.0
            cost_multiplier_input = cost_info['input_cost'] / base_input
            cost_multiplier_output = cost_info['output_cost'] / base_output
            
            if cost_multiplier_input == 1.0:
                cost_comparison = 'Baseline (cheapest)'
            else:
                avg_multiplier = (cost_multiplier_input + cost_multiplier_output) / 2
                percent_increase = int((avg_multiplier - 1) * 100)
                cost_comparison = f'+{percent_increase}% cost vs Haiku ({int(cost_multiplier_input)}x input, {int(cost_multiplier_output)}x output)'
            
            available_models.append({
                'id': model_id,
                'name': model_id.replace('-', ' ').title(),
                'description': cost_info['description'],
                'use_case': cost_info['use_case'],
                'cost_detail': f"${int(cost_info['input_cost'])} in / ${int(cost_info['output_cost'])} out per million tokens",
                'cost_comparison': cost_comparison,
                'input_cost': cost_info['input_cost'],
                'output_cost': cost_info['output_cost']
            })
        
        # Sort by cost
        available_models.sort(key=lambda x: x['input_cost'] + x['output_cost'])
    
    return available_models


def analyze_with_narrative(
    metrics: Dict[str, int],
    previous: Optional[Dict[str, int]] = None,
    changes: Optional[Dict[str, float]] = None,
    mode: str = 'Free',
    model: str = 'claude-sonnet-4-20250514',
    severity_results: Optional[Dict] = None,
    custom_thresholds: Optional[Dict] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate narrative analysis using selected mode.
    
    Args:
        metrics: Current metric values
        previous: Previous metric values (optional)
        changes: Calculated changes (optional)
        mode: 'Free' for rule-based or 'Claude AI' for API-based narratives
        model: Claude model ID (only used if mode is 'Claude AI')
        severity_results: Pre-computed severity analysis (optional, for Free mode)
        custom_thresholds: Custom threshold dict (optional, for Free mode)
    
    Returns:
        (narrative, error_message) - narrative is None if error occurred
    """
    # Route based on mode
    if mode == 'Free':
        try:
            narrative = build_local_narrative(
                metrics, 
                previous, 
                changes,
                severity_results=severity_results,
                custom_thresholds=custom_thresholds
            )
            return narrative, None
        except Exception as e:
            return None, f"❌ Error generating local narrative: {str(e)}"
    
    elif mode == 'Claude AI':
        if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == 'your_key_here':
            return None, "⚠️ Claude AI mode requires API key. Add ANTHROPIC_API_KEY to your .env file or switch to Free mode."
        
        prompt = build_context_prompt(metrics, previous, changes)
        
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            message = client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text, None
        except Exception as e:
            return None, f"❌ Error calling Claude API: {str(e)}"
    
    else:
        return None, f"❌ Unknown mode: {mode}"

def update_narrative_with_feedback(date, feedback):
    save_narrative(date, None, feedback)
    return True
