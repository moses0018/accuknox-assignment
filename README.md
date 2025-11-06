Accuknox Trainee Assignment
Topic: Django Signals
Question 1: By default are django signals executed synchronously or asynchronously?
By default, Django signals are executed synchronously.
Logic:​‍​‌‍​‍‌​‍​‌‍​‍‌ The code below demonstrates this. A signal receiver sync_receiver that sleeps for 2 seconds is defined. When the main function test_sync sends the signal, it prints a message before and after the .send() call. 

It will be printed that the "After sending signal..." message is only 
Code:

import time
from django.dispatch import Signal, receiver
my_signal = Signal()
@receiver(my_signal)
def sync_receiver(sender, **kwargs):
    print("    [Receiver]: Signal received. Going to sleep for 2 seconds...")
    time.sleep(2)
    print("    [Receiver]: Woke up. Finishing signal handler.")
def test_sync():
    print("[Main]: Before sending signal...")
    start_time = time.time()
    my_signal.send(sender=None)
    end_time = time.time()
    print(f"[Main]: After sending signal. Total time blocked: {end_time - start_time:.2f}s")

EXPECTED OUTPUT:
[Main]: Before sending signal...
    [Receiver]: Signal received. Going to sleep for 2 seconds...
    (...a 2-second pause occurs here...)
    [Receiver]: Woke up. Finishing signal handler.
[Main]: After sending signal. Total time blocked: 2.00s
"""


Question 2: Do django signals run in the same thread as the caller?
Yes, Django signals are executed in the same thread as the caller. This is a direct result of them being synchronous. 
Logic: The code below acquires the ID of the current thread (the "caller" thread) by threading.current_thread().ident. Then, it prints the thread ID from the signal receiver context. 
The output will demonstrate that the thread ID of the caller and the thread ID inside the receiver are the same, thus confirming that they are the same thread. 
Code:
import threading
from django.dispatch import Signal, receiver
my_signal = Signal()
@receiver(my_signal)
def thread_receiver(sender, **kwargs):
    receiver_thread_id = threading.current_thread().ident
    print(f"    [Receiver]: Running in thread ID: {receiver_thread_id}")
def test_thread():
    caller_thread_id = threading.current_thread().ident
    print(f"[Main]: Caller is running in thread ID: {caller_thread_id}")
    print("[Main]: Sending signal...")
    my_signal.send(sender=None)
    print("[Main]: Signal sent.")
"""
EXPECTED OUTPUT:
[Main]: Caller is running in thread ID: 140455827367680
[Main]: Sending signal...
    [Receiver]: Running in thread ID: 140455827367680
[Main]: Signal sent.

Question 3: By default do django signals run in the same database transaction as the caller?
Yes, by default, Django signals run in the same database transaction as the caller. 

Logic: This is the most conclusive proof.

We perform a model creation (MyModel.objects.create) inside a transaction.atomic() block. 

There is a post_save signal receiver (rollback_receiver) listening to this model's creation. 

We, in the receiver, raise an Exception on purpose. 

The exception goes all the way up and causes the transaction.atomic() block to be rolled back entirely, because the signal is executed in the same transaction. 

We catch the exception in the except block. 

At the end, we interrogate the database. If the object is not present (count is 0), that means that the signal's exception caused the rollback of the caller's create operation, which can only happen if they are sharing a ​‍​‌‍​‍‌​‍​‌‍​‍‌transaction. 
Code:
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MyModel
@receiver(post_save, sender=MyModel)
def rollback_receiver(sender, instance, created, **kwargs):
    if created:
        print(f"    [Receiver]: Signal received for created object (PK: {instance.pk}).")
        print("    [Receiver]: Object IS visible inside transaction.")
        print("    [Receiver]: Now raising an exception to force rollback...")
        raise ValueError("Intentional rollback from signal!")
def test_transaction():
    MyModel.objects.all().delete()
    print("[Main]: DB cleared.")
    try:
        with transaction.atomic():
            print("[Main]: Inside atomic block. Creating object...")
            MyModel.objects.create(name="Test Object")
            print("[Main]: This line should NOT be reached.")  
    except ValueError as e:
        print(f"[Main]: Caught expected exception: {e}"
    count = MyModel.objects.filter(name="Test Object").count()
    print(f"\n[Main]: After transaction, object count in DB: {count}")
    if count == 0:
        print("[Main]: PROOF: The object was rolled back. Signal runs in the same transaction.")
    else:
        print("[Main]: FAILED: The object was committed. Signal ran in a different transaction.")
"""
EXPECTED OUTPUT:
[Main]: DB cleared.
[Main]: Inside atomic block. Creating object...
    [Receiver]: Signal received for created object (PK: 1).
    [Receiver]: Object IS visible inside transaction.
    [Receiver]: Now raising an exception to force rollback...
[Main]: Caught expected exception: Intentional rollback from signal!

[Main]: After transaction, object count in DB: 0
[Main]: PROOF: The object was rolled back. Signal runs in the same transaction.
"""
