import simpy
import random

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
wood_capacity = 500
initial_wood = 100

    #electronic
electronic_capacity = 200
initial_electronic = 200

    #paint
pre_paint_capacity = 100
post_paint_capacity = 200
    
    #dispatch
dispatch_capacity = 500


#employees per activity
    #body
num_body = 2
mean_body = 1
std_body = 0.1

    #neck
num_neck = 1
mean_neck = 1
std_neck = 0.2

    #paint
num_paint = 1
mean_paint = 4
std_paint = 0.3

    #ensambling
num_ensam = 4
mean_ensam = 1
std_ensam = 0.2


#critical levels
    #critical stock should be 1 business day greater than supplier take to come
wood_critial_stock = (((8/mean_body) * num_body +
                      (8/mean_neck) * num_neck) * 3) #2 days to deliver + 1 marging

electronic_critical_stock = (8/mean_ensam) * num_ensam * 2 #1 day to deliver + 1 marging




#-------------------------------------------------

class Guitar_Factory:
    def __init__(self, env):
        self.wood = simpy.Container(env, capacity = wood_capacity, init = initial_wood)
        self.wood_control = env.process(self.wood_stock_control(env))
        self.electronic = simpy.Container(env, capacity = electronic_capacity, init = initial_electronic)
        self.electronic_control = env.process(self.electronic_stock_control(env))
        self.pre_paint = simpy.Container(env, capacity = pre_paint_capacity, init = 0)
        self.post_paint = simpy.Container(env, capacity = post_paint_capacity, init = 0)
        self.dispatch = simpy.Container(env ,capacity = dispatch_capacity, init = 0)

        
    def wood_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.wood.level <= wood_critial_stock:
                print('wood stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.wood.level, int(env.now/8), env.now % 8))
                print('calling wood supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('wood supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.wood.put(300)
                print('new wood stock is {0}'.format(
                    self.wood.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
    
    def electronic_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.electronic.level <= electronic_critical_stock:
                print('electronic stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.electronic.level, int(env.now/8), env.now % 8))
                print('calling electronic supplier')
                print('----------------------------------')
                yield env.timeout(9)
                print('electronic supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.electronic.put(30)
                print('new electronic stock is {0}'.format(
                    self.electronic.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
            
        
        
def body_maker(env, guitar_factory):
    while True:
        yield guitar_factory.wood.get(1)
        body_time = random.gauss(mean_body, std_body)
        yield env.timeout(body_time)
        yield guitar_factory.pre_paint.put(1)

def neck_maker(env, guitar_factory):
    while True:
        yield guitar_factory.wood.get(1)
        neck_time = random.gauss(mean_neck, std_neck)
        yield env.timeout(neck_time)
        yield guitar_factory.pre_paint.put(2)
        
def painter(env, guitar_factory):
    while True:
        yield guitar_factory.pre_paint.get(10)
        paint_time = random.gauss(mean_paint, std_paint)
        yield env.timeout(paint_time)
        yield guitar_factory.post_paint.put(10)

def assembler(env, guitar_factory):
    while True:
        yield guitar_factory.post_paint.get(1)
        yield guitar_factory.electronic.get(1)
        assembling_time = max(random.gauss(mean_ensam, std_ensam), 1)
        yield env.timeout(assembling_time)
        yield guitar_factory.dispatch.put(1)
        
        
#Generators
        
def body_maker_gen(env, guitar_factory):
    for i in range(num_body):
        env.process(body_maker(env, guitar_factory))
        yield env.timeout(0)

def neck_maker_gen(env, guitar_factory):
    for i in range(num_neck):
        env.process(neck_maker(env, guitar_factory))
        yield env.timeout(0)

def painter_maker_gen(env, guitar_factory):
    for i in range(num_paint):
        env.process(painter(env, guitar_factory))
        yield env.timeout(0)

def assembler_maker_gen(env, guitar_factory):
    for i in range(num_ensam):
        env.process(assembler(env, guitar_factory))
        yield env.timeout(0)


#-------------------------------------------------
        

env = simpy.Environment()
guitar_factory = Guitar_Factory(env)

body_gen = env.process(body_maker_gen(env, guitar_factory))
neck_gen = env.process(neck_maker_gen(env, guitar_factory))
painter_gen = env.process(painter_maker_gen(env, guitar_factory))
assembler_gen = env.process(assembler_maker_gen(env, guitar_factory))

env.run(until = total_time)

print(f'Pre paint has %d bodys and necks ready to be painted' % guitar_factory.pre_paint.level)
print(f'Post paint has %d bodys and necks ready to be assembled' % guitar_factory.post_paint.level)
print(f'Dispatch has %d guitars ready to go!' % guitar_factory.dispatch.level)
print(f'----------------------------------')
print(f'SIMULATION COMPLETED')
