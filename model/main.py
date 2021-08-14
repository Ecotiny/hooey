import numpy as np
import matplotlib.pyplot as plt
import yaml
import seaborn as sns
sns.set_theme('paper')

def get_config(fn='config.yml'):
    config = {}
    with open(fn, 'r') as f:
        doc = f.read()
        config = yaml.load(doc, Loader=yaml.Loader)
    return config

class Obj:
    def __init__(self, config):
        self.config = config
        self.gen_mass()
        self.gen_diameter()
        self.gen_distance()
        self.gen_velocity()
        self.gen_tang_vel()
        self.gen_ang_diam()
        self.gen_time()
    
    def gen_mass(self):
        max_mass = self.config['mass_dist']['maximum_mass']
        min_mass = self.config['mass_dist']['minimum_mass']
        self.mass = np.random.exponential(max_mass - min_mass) + min_mass

    def gen_diameter(self):
        density = self.config['mass_dist']['avg_density'] 
        volume = self.mass * 1e6 / density # volume in cubic kilometres 
        self.diameter = 2 * ((3*(volume)/(4*np.pi))**(1/3)) # mass comes in Tkg, diameter ends up in km
    
    def gen_distance(self):
        min_dist = self.config['field']['minimum_distance']
        max_dist = self.config['field']['maximum_distance'] # maybe later, calculate maximum distance to be constrained by diameter
        self.distance = (np.random.power(3) * (max_dist - min_dist)) + min_dist
        #np.random.uniform(min_dist, max_dist**(1/2)) ** 3 # volume is proportional to d^2 so, generate a distance with probability d^2
        # distance is in AU, velocity and diameter is in km (s^-1)
        self.distance_km = self.distance * 1.496e8

    def gen_velocity(self):
        min_spd = self.config['velocity']['minimum_speed'] 
        max_spd = self.config['velocity']['maximum_speed'] 
        vel_unit = np.random.random(3) # 3 axes
        self.velocity = vel_unit * np.random.uniform(min_spd, max_spd)

    def gen_tang_vel(self): # transverse angular velocity
        trv_vel = np.sqrt(self.velocity[0]**2 + self.velocity[1]**2) # x component, let's say
        self.tang_vel = np.arctan(trv_vel / self.distance_km) # in radians

    def gen_ang_diam(self): # angular diameter
        self.ang_diam = np.arctan(self.diameter / self.distance_km) # also in radians
    
    def gen_time(self): # calculate time of transit, assuming stars are infinitely far away...?
        self.time = self.ang_diam / self.tang_vel # in seconds
        

if __name__ == "__main__":
    config = get_config()
    distances = []
    diameters = []
    transit_t = []
    mass_dist = []
    n = int(1e6)

    density = True
    bins = 50 

    print(f"Generating {n}")
    for i in range(n):
        obj = Obj(config)
        distances.append(obj.distance) # au
        diameters.append(obj.diameter) # km
        transit_t.append(obj.time) # seconds
        mass_dist.append(obj.mass) # Tkg
        del obj
    print("Done!")

    fig, ((mass, dist), (diam, time)) = plt.subplots(2, 2)

    fig.suptitle(rf"$n = ${n}")

    mass.set_xlabel("Mass (Tkg)")
    dist.set_xlabel("Distance (AU)")
    diam.set_xlabel("Diameter (km)")
    time.set_xlabel("Transit (s)")

    time.set_xlim(0, 2.5)

    for axis in [mass, dist, diam, time]:
        axis.grid()

    mass.hist(mass_dist, bins=bins, density=density)
    dist.hist(distances, bins=bins, density=density)
    diam.hist(diameters, bins=bins, density=density)
    time.hist(transit_t, bins=bins, density=density, range=(0,2.5))

    plt.subplots_adjust(hspace=0.3, wspace=0.25)
    plt.savefig("histograms.png")
    plt.show()
    plt.clf()
    plt.hist2d(distances, transit_t, range=((0, 50), (0, 1)), density=density, bins=bins)
    plt.ylabel("Transit (s)")
    plt.xlabel("Distance (AU)")
    plt.savefig("histogram2d.png")
    plt.show()
        

