from data_loader import load_index
import os

def main():
    freq_dict = load_index()
    if not freq_dict:
        print("Index not found. Run data_loader.py first.")
        return
    
    print("=" * 60)
    print("Hindi Spell Checker")
    print("=" * 60)
    print(f"Dictionary loaded with {len(freq_dict)} words")
    print("\nProcessing input.txt file -> output.txt")
    
    process_file_option()

def process_file_option():
    input_file = "input.txt"
    output_file = "output.txt"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    print(f"Processing {input_file} -> {output_file}...")
    
    try:
        from file_processor import process_input_file
        process_input_file(input_file, output_file)
    except ImportError:
        print("Error: file_processor.py not found!")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == '__main__':
    main()