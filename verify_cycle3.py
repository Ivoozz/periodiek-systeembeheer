
import threading
import time
from app.db.database import engine, SessionLocal, Base
from app.db.models import Customer

def worker(worker_id):
    db = SessionLocal()
    try:
        # Each worker tries to create a customer
        name = f"Worker_{worker_id}_{time.time()}"
        customer = Customer(name=name, location="Concur_Test")
        db.add(customer)
        db.commit()
        print(f"Worker {worker_id} successfully added {name}")
    except Exception as e:
        print(f"Worker {worker_id} FAILED: {e}")
    finally:
        db.close()

def run_stress_test(num_threads=20):
    print(f"Starting stress test with {num_threads} threads...")
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    print("Stress test completed.")

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    run_stress_test(50) # Increase load
