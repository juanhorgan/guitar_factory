import simpy

print(f'STARTING SIMULATION')
print(f'----------------------------------')

#-------------------------------------------------

#Parameters

#working hours
hours = 8

#business days
days = 5

#total working time (hours)
total_time = hours * days

#containers
    #wood
wood_capacity = 1000
initial_wood = 500

    #dispatch
dispatch_capacity = 500



#-------------------------------------------------

class Guitar_Factory:
    def __init__(self, env):
        self.wood = simpy.Container(env, capacity = wood_capacity, init = initial_wood)
        self.dispatch = simpy.Container(env ,capacity = dispatch_capacity, init = 0)
        
def body_maker(env, guitar_factory):
    while True:
        yield guitar_factory.wood.get(1)
        body_time = 1
        yield env.timeout(body_time)
        yield guitar_factory.dispatch.put(1)

def neck_maker(env, guitar_factory):
    while True:
        yield guitar_factory.wood.get(1)
        neck_time = 1
        yield env.timeout(neck_time)
        yield guitar_factory.dispatch.put(2)


#-------------------------------------------------
        

env = simpy.Environment()
guitar_factory = Guitar_Factory(env)

body_maker_process = env.process(body_maker(env, guitar_factory))
neck_maker_process = env.process(neck_maker(env, guitar_factory))


env.run(until = total_time)


print(f'Dispatch has %d bodies and necks ready to go!' % guitar_factory.dispatch.level)
print(f'----------------------------------')
print(f'SIMULATION COMPLETED')
