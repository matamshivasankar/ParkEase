import sys
sys.path.insert(0, '.')

from backend.seed_data import seed_data

if __name__ == '__main__':
    seed_data(reset='--reset' in sys.argv)
