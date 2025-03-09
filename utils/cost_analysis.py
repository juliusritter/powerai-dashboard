def calculate_cost_impact(equipment):
    """
    Calculate cost impact and potential savings
    Returns dictionary with cost breakdowns
    """
    try:
        # Base costs
        base_maintenance_cost = 1000  # Base cost for preventative maintenance
        base_repair_cost = 5000      # Base cost for repairs after failure
        
        # Adjust costs based on equipment age
        age_factor = min(equipment['age'] / 10, 2)  # Max 2x cost for old equipment
        
        # Adjust costs based on customer impact
        customer_factor = 1 + (equipment['customer_impact'] / 1000)
        
        # Calculate final costs
        preventative_cost = base_maintenance_cost * age_factor
        repair_cost = base_repair_cost * age_factor * customer_factor
        
        # Calculate potential savings
        savings = repair_cost - preventative_cost
        
        return {
            'preventative_cost': preventative_cost,
            'repair_cost': repair_cost,
            'savings': savings
        }
        
    except Exception as e:
        raise Exception(f"Error calculating cost impact: {str(e)}")

def calculate_customer_impact_cost(customer_count):
    """Calculate cost impact based on number of affected customers"""
    try:
        # Base cost per customer per hour of outage
        cost_per_customer_hour = 10
        
        # Assume average outage duration of 4 hours
        average_outage_duration = 4
        
        total_impact = customer_count * cost_per_customer_hour * average_outage_duration
        
        return total_impact
        
    except Exception as e:
        raise Exception(f"Error calculating customer impact cost: {str(e)}")
