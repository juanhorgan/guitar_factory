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
    #electronic
electronic_capacity = 100
initial_electronic = 100
    #paint
pre_paint_capacity = 100
post_paint_capacity = 200    
    #dispatch
dispatch_capacity = 500

#-------------------------------------------------

class Guitar_Factory:
    def __init__(self, env):
        self.wood = simpy.Container(env, capacity = wood_capacity, init = initial_wood)
        self.electronic = simpy.Container(env, capacity = electronic_capacity, init = initial_electronic)
        self.pre_paint = simpy.Container(env, capacity = pre_paint_capacity, init = 0)
        self.post_paint = simpy.Container(env, capacity = post_paint_capacity, init = 0)
        self.dispatch = simpy.Container(env ,capacity = dispatch_capacity, init = 0)
                
def body_maker(env, guitar_factory):
    while True:
        yield guitar_factory.wood.get(1)
        body_time = 1
        yield env.timeout(body_time)
        yield guitar_factory.pre_paint.put(1)

def neck_maker(env, guitar_factory):
    while True:
        yield guitar_factory.wood.get(1)
        neck_time = 1
        yield env.timeout(neck_time)
        yield guitar_factory.pre_paint.put(2)
        
def painter(env, guitar_factory):
    while True:
        yield guitar_factory.pre_paint.get(10)
        paint_time = 4
        yield env.timeout(paint_time)
        yield guitar_factory.post_paint.put(10)

def assembler(env, guitar_factory):
    while True:
        yield guitar_factory.post_paint.get(2)
        yield guitar_factory.electronic.get(1)
        assembling_time = 1
        yield env.timeout(assembling_time)
        yield guitar_factory.dispatch.put(1)

#-------------------------------------------------
        

env = simpy.Environment()
guitar_factory = Guitar_Factory(env)

body_maker_process = env.process(body_maker(env, guitar_factory))
neck_maker_process = env.process(neck_maker(env, guitar_factory))
painter_process = env.process(painter(env, guitar_factory))
assembler_process = env.process(assembler(env, guitar_factory))

env.run(until = total_time)

print(f'Pre paint has %d bodies and necks ready to be painted' % guitar_factory.pre_paint.level)
print(f'Post paint has %d bodies and necks ready to be assembled' % guitar_factory.post_paint.level)
print(f'Dispatch has %d guitars ready to go!' % guitar_factory.dispatch.level)
print(f'----------------------------------')
print(f'SIMULATION COMPLETED')
