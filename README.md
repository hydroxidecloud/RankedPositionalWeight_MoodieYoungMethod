# Ranked-Positional-Weight_Moodie-Young-Method

This project aims to optimize assembly line balancing for specific models by minimizing the number of workstations while adhering to given cycle time constraints. The project implements two methods to achieve this goal: Ranked Positional Weight (RPW) and the Moodie Young Method (MYM).

## Project Structure

The project includes the following components:

- **Code**: Python scripts implementing two methods:
  - `01RPW.py`: Implements the Ranked Positional Weight method.
  - `02MYM_classic.py`: Implements the classic Moodie Young Method.
  - `04MYM_*.py`: Implements modified versions of the Moodie Young Method for exploratory purposes.

## Implemented Methods

### RPW - Ranked Positional Weight Method

RPW is a heuristic method that assigns tasks to workstations based on weighted positional values within the assembly line sequence. The algorithm aims to minimize the required number of workstations while meeting cycle time constraints.

### MYM - Moodie Young Method

MYM consists of two main stages:

1. **Work Elements Assignment Stage**: Tasks are assigned to workstations based on specific task sequencing rules to explore their impact on workstation count.
2. **Trade and Transfer Stage**: By evaluating different rules for selecting workstations during trades and transfers, further optimization of workstation allocation is achieved to balance the assembly line.

## Experimental Exploration

### Impact of Task Sequencing Rules on Work Elements Assignment Stage

Different task sequencing rules significantly affect the number of workstations required in the work elements assignment stage. This project explores various task sequencing strategies to determine which effectively minimizes the number of workstations.

### Impact of Workstation Selection Rules on Trade and Transfer Stage

During the trade and transfer stage, rules for selecting workstations influence the balance index of the assembly line. This project studies these rules to ascertain their impact on achieving optimal workstation allocation.

## Usage

1. **Data Preparation**: Ensure the CSV file containing detailed task information is correctly formatted and named `tasks.csv`.
   >ID,Name,Time,Predecessors
   >
   >...
   >
   >26,Install Right Bumper,5,25
   >
   >27,Prepare for Pairing,5,24;26
   >
   >28,Connect Crossbeam with Engine,40,11;13;27

2. **Execution**:
   - Run `01RPW.py` to apply the Ranked Positional Weights method.
   - Run `02MYM_classic.py` to apply the classic Moodie Young Method.
