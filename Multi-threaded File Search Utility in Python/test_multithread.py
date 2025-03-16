from file_search import main
import sys
import time
import re

#Part 2, Performance Analysis
def test_performance():
    keyword = 'python'
    dir = 'all_txt_file_sample'
    #multithread
    start_mt = time.time()
    main(dir, keyword, 4)
    end_mt = time.time()
    time_mt = end_mt - start_mt

    #Single thread
    start_st = time.time()
    main(dir, keyword, 1)
    end_st = time.time()
    time_st = end_st - start_st

    # Calculate percentage improvement
    percentage_improvement = ((time_st - time_mt) / time_st) * 100

    print(f"Multithread time: {time_mt} seconds")
    print(f"Single thread time: {time_st} seconds")
    print(f"Performance improvement: {percentage_improvement:.2f}%")



#Test keyword 'python' dalam file
def test_python_keyword():
    keyword = 'python'
    dir = 'all_txt_file_sample'
    expected = [('all_txt_file_sample\\Abraham Silberschatz-Operating System Concepts (10th,2018).txt', 2), ('all_txt_file_sample\\Introduction_to_Python_Programming_-_WEB.txt', 280), ('all_txt_file_sample\\Week 2 - Operating System Structure.txt', 2), ('all_txt_file_sample\\Week 4 - Threads.txt', 1)]
    shared_list = main(dir, keyword, 4)

    assert shared_list == expected

#test dengan banyak file 
def test_multiple_files():
    all_thread  = [] 
    keyword = 'uhuy'
    dir = 'all_txt_file_sample'

    def thread_info():
        for thread_id, frame in sys._current_frames().items():
            if thread_id not in all_thread:
                all_thread.append(thread_id) #masukkan semua unique thread_id

    main(dir, keyword, max_threads=4, thread_info=thread_info)
    expected = 5 #4 worker threads + 1 main thread

    #Thread_id unique yang tercatat harus 5 
    assert len(all_thread) == expected

#Test apakah multithread berjalan dengan 2,4,6,8 thread
def test_thread_management():
    keyword = 'uhuy'
    dir = 'all_txt_file_sample'
    for i in [2,4,6,8]:
        main(dir, keyword, i)
    
    assert True

def test_regex():
    keyword = re.compile(r'\bpython\b', re.IGNORECASE)
    dir = 'all_txt_file_sample'
    main(dir, keyword, 4)

def test_non_existent_dir():
    keyword = "hello"
    dir = "xxxxx"
    main(dir, keyword, 4)

def test_no_text_files():
    keyword = "hello"
    dir = "blank_folder_test"
    main(dir, keyword, 4)

def test_no_match():
    keyword = "xxxxxxxxx"
    dir = "all_txt_file_sample"
    main(dir, keyword, 4)

def run():
    test_python_keyword()
    test_multiple_files()
    test_thread_management()
    test_performance()
    test_regex()
    test_non_existent_dir()
    test_no_text_files()
    test_no_match()

    print('All test passed')


if __name__ == "__main__":
    run()