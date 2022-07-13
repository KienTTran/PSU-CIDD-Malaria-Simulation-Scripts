# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 12:27:54 2022

@author: kient
"""
import kfp
import kfp.components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

@comp.func_to_container_op
def print_small_text(text: str):
    '''Print small text'''
    print(text)

@comp.func_to_container_op
def produce_one_small_output() -> str:
    return 'Hello world'

def constant_to_consumer_pipeline():
    '''Pipeline that passes small constant string to to consumer'''
    consume_task = print_small_text('Hello world') # Passing constant as argument to consumer
    
def task_output_to_consumer_pipeline():
    '''Pipeline that passes small data from producer to consumer'''
    produce_task = produce_one_small_output()
    # Passing producer task output as argument to consumer
    consume_task1 = print_small_text(produce_task.output) # task.output only works for single-output components
    consume_task2 = print_small_text(produce_task.outputs['output']) # task.outputs[...] always works
    consume_task = print_small_text('kkkkk')

client.create_run_from_pipeline_func(task_output_to_consumer_pipeline, arguments={})

#%%
from typing import NamedTuple
import kfp
import kfp.components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

@comp.func_to_container_op
def produce_two_small_outputs() -> NamedTuple('Outputs', [('text', str), ('number', int)]):
    return ("data 1", 42)

@comp.func_to_container_op
def consume_two_arguments(text: str, number: int):
    print('Text={}'.format(text))
    print('Number={}'.format(str(number)))

def producers_to_consumers_pipeline(text: str = "Hello world"):
    '''Pipeline that passes data from producer to consumer'''
    produce1_task = produce_one_small_output()
    produce2_task = produce_two_small_outputs()

    consume_task1 = consume_two_arguments(produce1_task.output, 42)
    consume_task2 = consume_two_arguments(text, produce2_task.outputs['number'])
    consume_task3 = consume_two_arguments(produce2_task.outputs['text'], produce2_task.outputs['number'])

client.create_run_from_pipeline_func(producers_to_consumers_pipeline, arguments={})

#%%
from typing import NamedTuple
import kfp
import kfp.components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

@comp.func_to_container_op
def get_item_from_list(list_of_strings: list, index: int) -> str:
    return list_of_strings[index]

@comp.func_to_container_op
def truncate_text(text: str, max_length: int) -> str:
    return text[0:max_length]

def processing_pipeline(text: str = "Hello world"):
    truncate_task = truncate_text(text, max_length=5)
    get_item_task = get_item_from_list(list_of_strings=[3, 1, truncate_task.output, 1, 5, 9, 2, 6, 7], index=2)
    print_small_text(get_item_task.output)


client.create_run_from_pipeline_func(processing_pipeline, arguments={})

#%%
from typing import NamedTuple
import kfp
import kfp.components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

# Writing bigger data
@comp.func_to_container_op
def repeat_line(line: str, output_text_path: comp.OutputPath(str), count: int = 10):
    '''Repeat the line specified number of times'''
    with open(output_text_path, 'w') as writer:
        for i in range(count):
            writer.write(line + '\n')


# Reading bigger data
@comp.func_to_container_op
def print_text(text_path: comp.InputPath()): # The "text" input is untyped so that any data can be printed
    '''Print text'''
    with open(text_path, 'r') as reader:
        for line in reader:
            print(line, end = '')

def print_repeating_lines_pipeline():
    repeat_lines_task = repeat_line(line='Hello', count=5000)
    print_text(repeat_lines_task.output) # Don't forget .output !

client.create_run_from_pipeline_func(print_repeating_lines_pipeline, arguments={})

#%%
from typing import NamedTuple
import kfp
import kfp.components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

@comp.func_to_container_op
def split_text_lines(source_path: comp.InputPath(str), odd_lines_path: comp.OutputPath(str), even_lines_path: comp.OutputPath(str)):
    with open(source_path, 'r') as reader:
        with open(odd_lines_path, 'w') as odd_writer:
            with open(even_lines_path, 'w') as even_writer:
                while True:
                    line = reader.readline()
                    if line == "":
                        break
                    odd_writer.write(line)
                    line = reader.readline()
                    if line == "":
                        break
                    even_writer.write(line)

def text_splitting_pipeline():
    text = '\n'.join(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
    split_text_task = split_text_lines(text)
    print_text(split_text_task.outputs['odd_lines'])
    print_text(split_text_task.outputs['even_lines'])

client.create_run_from_pipeline_func(text_splitting_pipeline, arguments={})

#%%
from typing import NamedTuple
import kfp
import kfp.components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

@comp.func_to_container_op
def split_text_lines2(source_file: comp.InputTextFile(str), odd_lines_file: comp.OutputTextFile(str), even_lines_file: comp.OutputTextFile(str)):
    while True:
        line = source_file.readline()
        if line == "":
            break
        odd_lines_file.write(line)
        line = source_file.readline()
        if line == "":
            break
        even_lines_file.write(line)

def text_splitting_pipeline2():
    text = '\n'.join(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
    split_text_task = split_text_lines2(text)
    print_text(split_text_task.outputs['odd_lines']).set_display_name('Odd lines')
    print_text(split_text_task.outputs['even_lines']).set_display_name('Even lines')

client.create_run_from_pipeline_func(text_splitting_pipeline2, arguments={})

#%%
from typing import NamedTuple
import kfp
import kfp.components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

# Writing many numbers
@comp.func_to_container_op
def write_numbers(numbers_path: comp.OutputPath(str), start: int = 0, count: int = 10):
    with open(numbers_path, 'w') as writer:
        for i in range(start, count):
            writer.write(str(i) + '\n')


# Reading and summing many numbers
@comp.func_to_container_op
def sum_numbers(numbers_path: comp.InputPath(str)) -> int:
    sum = 0
    with open(numbers_path, 'r') as reader:
        for line in reader:
            sum = sum + int(line)
    return sum

# Pipeline to sum 100000 numbers
def sum_pipeline(count: int = 100000):
    numbers_task = write_numbers(count=count)
    print_text(numbers_task.output)

    sum_task = sum_numbers(numbers_task.outputs['numbers'])
    print_text(sum_task.output)


# Running the pipeline
client.create_run_from_pipeline_func(sum_pipeline, arguments={})

#%%

import kfp
from kfp import dsl
from kfp import components as comp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

def add(a: float, b: float, f: comp.OutputTextFile()):
    '''Calculates sum of two arguments'''
    sum_ = a + b
    f.write(str(sum_)) # cast to str
    return sum_


def multiply(c: float, d: float, f: comp.InputTextFile()):
    '''Calculates the product'''
    in_ = float(f.read()) # cast to float
    product = c * d * in_
    print(product)
    return product


add_op = comp.func_to_container_op(add,
                                   output_component_file='add_component.yaml')
product_op = comp.create_component_from_func(
    multiply, output_component_file='multiple_component.yaml')


@dsl.pipeline(
    name='Addition-pipeline',
    description='An example pipeline that performs addition calculations.')
def my_pipeline(a='8', b='7', c='4', d='1'):
    first_add_task = add_op(a, b)
    second_add_task = product_op(c, d, first_add_task.output)
    
# Running the pipeline
client.create_run_from_pipeline_func(my_pipeline, arguments={})