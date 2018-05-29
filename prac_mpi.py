from mpi4py import MPI
import random
import numpy as np

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
status = MPI.Status()
# first element is data and second is flag
# flag is used to send the generated num to next node
randNum = np.zeros(2)
sent_once = True
max_num = None
max_leader = None
max_vote = None
max_vote_source = None
id_max = None
for p in range(2 * size):

    if rank == 0:
        if sent_once:
            # Generate a 64-bit random number
            randNum[0] = random.getrandbits(64)
            init_num = randNum[0]
            print('This is process %d with num %g' % (rank, randNum[0]))
            comm.Send(randNum, dest=1, tag=rank)
            sent_once = False
            # Synchronize all process
            comm.Barrier()
        comm.Recv(randNum, source=size - 1, status=status)
        recv_num = randNum[0]
        # print(recv_num)
        recv_tag = status.Get_tag()
        # print('it is {} and the recv num is {} from process {}'.format(
        #     rank, recv_num, recv_tag))

        recv_flag = randNum[1]
        if recv_flag != 0:
            print('It is process %d: The max value is %g from process %d' %
                  (rank, recv_num, recv_tag))

        if (recv_num != -1) and (recv_num > init_num):
            # send only if the prev node's num is larger
            comm.Send(randNum, dest=1, tag=recv_tag)
        elif (recv_num != -1) and (recv_tag == rank):
            max_num = recv_num
            max_leader = rank
            randNum[1] = 1
            comm.Send(randNum, dest=1, tag=rank)
            # print('I am process %d and I am max and it is %g' %
            #       (rank, recv_num))
        else:
            # otherwise send -1
            randNum[0] = -1
            comm.Send(randNum, dest=1, tag=rank)

    if rank == size - 1:
        if sent_once:
            # Generate a 64-bit random number
            randNum[0] = random.getrandbits(64)
            init_num = randNum[0]
            print('This is process %d with num %g' % (rank, randNum[0]))
            comm.Send(randNum, dest=0, tag=rank)
            sent_once = False
            # Synchronize all process
            comm.Barrier()
        comm.Recv(randNum, source=size - 2, status=status)
        recv_num = randNum[0]
        recv_tag = status.Get_tag()
        # print(recv_num)
        # print('it is {} and the recv num is {} from process {}'.format(
        #     rank, recv_num, recv_tag))

        recv_flag = randNum[1]
        if recv_flag != 0:
            print('It is process %d: The max value is %g from process %d' %
                  (rank, recv_num, recv_tag))

        if (recv_num != -1) and (recv_num > init_num):
            # send only if the prev node's num is larger
            comm.Send(randNum, dest=0, tag=recv_tag)
        elif (recv_num != -1) and (recv_tag == rank):
            max_num = recv_num
            max_leader = rank
            randNum[1] = 1
            comm.Send(randNum, dest=0, tag=rank)
            # print('I am process %d and I am max and it is %g' %
            #       (rank, recv_num))
        else:
            # otherwise send Nothing
            randNum[0] = -1
            comm.Send(randNum, dest=0, tag=rank)

    if (rank > 0) and (rank < size - 1):
        if sent_once:
            # Generate a 64-bit random number
            randNum[0] = random.getrandbits(64)
            init_num = randNum[0]
            print('This is process %d with num %g' % (rank, randNum[0]))
            comm.Send(randNum, dest=rank + 1, tag=rank)
            sent_once = False
            # Synchronize all process
            comm.Barrier()
        comm.Recv(randNum, source=rank - 1, status=status)
        recv_num = randNum[0]
        recv_tag = status.Get_tag()
        # print(recv_num)
        # print('it is {} and the recv num is {} from process {}'.format(
        #     rank, recv_num, recv_tag))

        recv_flag = randNum[1]
        if recv_flag != 0:
            print('It is process %d: The max value is %g from process %d' %
                  (rank, recv_num, recv_tag))

        if (recv_num != -1) and (recv_num > init_num):
            # send only if the prev node's num is larger
            comm.Send(randNum, dest=rank + 1, tag=recv_tag)
        elif (recv_num != -1) and (recv_tag == rank):
            max_num = recv_num
            max_leader = rank
            randNum[1] = 1
            comm.Send(randNum, dest=rank + 1, tag=rank)
            # print('I am process %d and I am max and it is %g' %
            #       (rank, recv_num))
        else:
            # otherwise send Nothing
            randNum[0] = -1
            comm.Send(randNum, dest=rank + 1, tag=rank)
