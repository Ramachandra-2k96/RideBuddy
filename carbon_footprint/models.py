from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_rides = models.IntegerField(default=0)
    total_co2_saved = models.FloatField(default=0)
    total_distance = models.FloatField(default=0)
    preferred_vehicle_type = models.CharField(max_length=20, null=True, blank=True)
    
    def update_profile_stats(self, ride):
        """Update user profile statistics after each ride"""
        self.total_rides += 1
        self.total_distance += ride.distance
        self.total_co2_saved += ride.co2_savings
        
        # Update preferred vehicle type
        if not self.preferred_vehicle_type:
            self.preferred_vehicle_type = ride.fuel_type
        else:
            # Simple logic to determine preferred vehicle type
            vehicle_counts = {
                'petrol': 0,
                'diesel': 0,
                'ev': 0
            }
            recent_rides = RideRecord.objects.filter(user=self.user).order_by('-ride_time')[:10]
            for recent_ride in recent_rides:
                vehicle_counts[recent_ride.fuel_type] += 1
            
            # Update preferred vehicle type based on most frequent
            self.preferred_vehicle_type = max(vehicle_counts, key=vehicle_counts.get)
        
        self.save()

class RideRecord(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('ev', 'Electric Vehicle')
    ]
    
    TRAFFIC_CHOICES = [
        ('light', 'Light Traffic'),
        ('moderate', 'Moderate Traffic'), 
        ('heavy', 'Heavy Traffic')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    distance = models.FloatField(help_text="Distance in kilometers")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    num_riders = models.IntegerField(default=1, help_text="Number of passengers")
    traffic_condition = models.CharField(max_length=20, choices=TRAFFIC_CHOICES)
    idle_time = models.IntegerField(default=0, help_text="Idle time in minutes")
    ride_time = models.DateTimeField()
    co2_emissions = models.FloatField(null=True, blank=True)
    co2_savings = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate emissions and savings before saving
        if not self.co2_emissions or not self.co2_savings:
            self.calculate_carbon_impact()
        
        super().save(*args, **kwargs)
        
        # Update user profile
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.update_profile_stats(self)

    def calculate_carbon_impact(self):
        """
        Comprehensive carbon impact calculation with enhanced precision
        """
        # Base emissions constants
        BASE_EMISSIONS_PER_KM = {
            'petrol': 251,   # grams CO2 per km
            'diesel': 289,   # 15% higher than petrol
            'ev': 0          # Zero direct emissions
        }
        
        # Traffic condition multipliers
        TRAFFIC_MULTIPLIERS = {
            'light': 1.0,    # No change
            'moderate': 1.1, # 10% increase
            'heavy': 1.2     # 20% increase
        }
        
        # Idle emissions
        IDLE_EMISSIONS_RATE = 10  # grams per minute
        
        # Nighttime efficiency (8 PM to 6 AM)
        def is_nighttime(ride_time):
            return 20 <= ride_time.hour or ride_time.hour < 6
        
        # Core calculation logic
        def calculate_emissions():
            # Base emissions based on fuel type and distance
            base_emissions = self.distance * BASE_EMISSIONS_PER_KM.get(self.fuel_type, 251)
            
            # Traffic condition adjustment
            traffic_multiplier = TRAFFIC_MULTIPLIERS.get(self.traffic_condition, 1.0)
            
            # Rider sharing reduction
            rider_reduction_factor = 1 - (1 / max(1, self.num_riders))
            
            # Nighttime efficiency
            nighttime_multiplier = 0.95 if is_nighttime(self.ride_time) else 1.0
            
            # Idle time emissions
            idle_emissions = self.idle_time * IDLE_EMISSIONS_RATE
            
            # Total emissions calculation
            total_emissions = (
                base_emissions * 
                traffic_multiplier * 
                rider_reduction_factor * 
                nighttime_multiplier
            ) + idle_emissions
            
            # Savings calculation (compared to single-occupancy vehicle)
            total_savings = base_emissions - total_emissions
            
            return total_emissions, total_savings
        
        # Calculate and store emissions
        self.co2_emissions, self.co2_savings = calculate_emissions()
        return self.co2_emissions, self.co2_savings
    
def get_user_eco_impact(user):
    """
    Retrieve comprehensive eco-impact statistics for a user
    """
    profile = UserProfile.objects.get(user=user)
    total_rides = RideRecord.objects.filter(user=user).count()
    total_distance = RideRecord.objects.filter(user=user).aggregate(
        total_distance=Sum('distance')
    )['total_distance'] or 0
    
    vehicle_breakdown = RideRecord.objects.filter(user=user).values('fuel_type').annotate(
        count=models.Count('fuel_type')
    )
    
    return {
        'total_rides': total_rides,
        'total_co2_saved': profile.total_co2_saved,
        'total_distance': total_distance,
        'preferred_vehicle': profile.preferred_vehicle_type,
        'vehicle_breakdown': list(vehicle_breakdown)
    }