import numpy as np
from mpi4py import MPI
import copy
import random

# The Yo-Yo algorithm for maximum consensus algorithm is implemented
#  The status indicator is needed to determine
# the end of iterative data transmission


def neigh_det(vertex, rank, num_conn, neigh):
    # This function construct a k-regular graph
    vertex = np.delete(vertex, rank)
    vertex = np.roll(vertex, -rank)
    # print(rank,vertex)
    if num_conn % 2 == 0:
        neigh[0:num_conn // 2] = vertex[size - (num_conn // 2) -
                                        1:size - 1]
        neigh[num_conn // 2: num_conn] = vertex[size:size +
                                                (num_conn // 2)]
    # in this case the number of nodes ashould be even,
    # otherwise there is no k-regular graph of a given degree
    elif num_conn % 2 != 0 and size % 2 == 0:
        neigh[0:num_conn // 2] = vertex[size - (num_conn // 2) -
                                        1:size - 1]
        neigh[num_conn // 2] = vertex[size + (size // 2) - 1]
        neigh[num_conn // 2 + 1: num_conn] = vertex[size:size +
                                                    (num_conn // 2)]
    else:
        raise Exception('There is no k-regular graph! Choose another value')

    return neigh


def send_msg(neigh, randNum, rank):
    # This function send msg to the neighbour nodes
    for i in range(len(neigh)):
        comm.Send(randNum, dest=neigh[i], tag=rank)


def recv_msg(neigh, randNum, rank, data_receive):
    # This function collects data from all neighbours
    for i in range(len(neigh)):
        comm.Recv(randNum, source=neigh[i], status=status)
        data_receive[:, i] = randNum
        recv_tag = status.Get_tag()
        data_receive_idx[i] = recv_tag
        # print('it is process %d from %d' %
        #       (rank, data_receive_idx[i]), data_receive[:, i])
    return data_receive, data_receive_idx


def status_neighbour(Recv, rand_in, rank):
    # This function determines status of the neighbours node
    idx_neigh = Recv[0][0]
    data_neigh = Recv[0][1]
    stat_neigh = dict()
    # 'in': inward arrow, 'out': outward arrow
    for j in range(len(idx_neigh)):
        if data_neigh[j] >= rand_in:
            stat_neigh[str(int(idx_neigh[j]))] = 'in'
        else:
            stat_neigh[str(int(idx_neigh[j]))] = 'out'
    # print('it is process', rank, stat_neigh)
    return stat_neigh


def status_itself(stat_neigh, num_conn):
    # This function determine the status of the node itself
    inward = 0
    outward = 0
    for value in stat_neigh:
        if stat_neigh[value] == 'in':
            inward += 1
        elif stat_neigh[value] == 'out':
            outward += 1
    if outward == num_conn:
        status_node = 'source'
    elif inward == num_conn:
        status_node = 'sink'
    else:
        status_node = 'internal'
    # print(inward, outward, status_node)
    return status_node, inward, outward


def set_flag(stat_it, rand_in):
    #  This func set the src flag to indicate source node
    if stat_it[0] == 'source':
        rand_in[2] = 1
    elif stat_it[0] == 'sink':
        rand_in[2] = 2
    elif stat_it[0] == 'internal':
        rand_in[2] = 0


def compare_in(Recv, rand_in, rank):
    #  This function compare the incoming data
    idx_neigh = np.append(Recv[0][0], rank)
    data_neigh = np.append(Recv[0][1], rand_in[1])
    max_vote = np.max(data_neigh)
    max_vote_idx = data_neigh.argmax()
    nom_max = idx_neigh[max_vote_idx]
    # print('it is process', rank, max_vote, nom_max)
    return max_vote, max_vote_idx, nom_max


if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    status = MPI.Status()
    # number of connected neighbors
    num_conn = int(size / 10)
    it = size
    neigh = np.zeros(num_conn)
    # all nodes
    vertex = np.arange(size)
    vertex = np.concatenate((vertex, vertex), axis=0)
    # first element is rank, second is data, and third is flag
    # default flag is zero, if sourse, flag is 1
    randNum = np.zeros(3)
    data_receive = np.zeros((3, num_conn))
    data_receive_idx = np.zeros(num_conn)
    max_vote = 0
    max_vote_idx = 0
    if rank == 0:
        randNum[0] = rank
        # Generate a 64-bit random number
        randNum[1] = random.getrandbits(64)
        rand_in = copy.deepcopy(randNum)
        neigh_det(vertex, rank, num_conn, neigh)
        print('It is process', rank, 'with neighbor nodes', neigh, 'and number', randNum[1])
        send_msg(neigh, randNum, rank)
        Recv = recv_msg(neigh, randNum, rank, data_receive)
        comm.Barrier()
        # print('it is process', rank, 'the Recv is', Recv[0][1])
        stat_n = status_neighbour(Recv, rand_in[1], rank)
        stat_it = status_itself(stat_n, num_conn)
        comm.Barrier()
        set_flag(stat_it, rand_in)
        # print('It is process', rank, 'and the status is',
        #       stat_it[0], 'with data', rand_in)
        comm.Barrier()
        # -------------------figure 3.53------------------
        for i in range(it):
            fo = compare_in(Recv, rand_in, rank)
            # print('It is process', rank, 'and the max is', fo[0])
            comm.Barrier()
            randNum = copy.deepcopy(rand_in)
            randNum[1] = fo[0]
            send_msg(neigh, randNum, rank)
            # print('It is process', rank, 'and the Sent is', randNum[1])
            Recv = recv_msg(neigh, randNum, rank, data_receive)
            comm.Barrier()
        print('it is the process', rank, 'and the max is', fo[0])

    if rank == size - 1:
        randNum[0] = rank
        randNum[1] = random.getrandbits(64)
        rand_in = copy.deepcopy(randNum)
        neigh_det(vertex, rank, num_conn, neigh)
        print('It is process', rank, 'with neighbor nodes', neigh, 'and number', randNum[1])
        send_msg(neigh, randNum, rank)
        Recv = recv_msg(neigh, randNum, rank, data_receive)
        comm.Barrier()
        # print('it is process', rank, 'the Recv is', Recv[0][1])
        stat_n = status_neighbour(Recv, rand_in[1], rank)
        stat_it = status_itself(stat_n, num_conn)
        comm.Barrier()
        set_flag(stat_it, rand_in)
        # print('It is process', rank, 'and the status is',
        #       stat_it[0], 'with data', rand_in)
        comm.Barrier()
        # -------------------figure 3.53------------------
        for i in range(it):
            fo = compare_in(Recv, rand_in, rank)
            # print('It is process', rank, 'and the max is', fo[0])
            comm.Barrier()
            randNum = copy.deepcopy(rand_in)
            randNum[1] = fo[0]
            send_msg(neigh, randNum, rank)
            # print('It is process', rank, 'and the Sent is', randNum[1])
            Recv = recv_msg(neigh, randNum, rank, data_receive)
            comm.Barrier()
        print('it is the process', rank, 'and the max is', fo[0])

    if (rank > 0) and (rank < size - 1):
        randNum[0] = rank
        randNum[1] = random.getrandbits(64)
        rand_in = copy.deepcopy(randNum)
        neigh_det(vertex, rank, num_conn, neigh)
        print('It is process', rank, 'with neighbor nodes', neigh, 'and number', randNum[1])
        send_msg(neigh, randNum, rank)
        Recv = recv_msg(neigh, randNum, rank, data_receive)
        comm.Barrier()
        # print('it is process', rank, 'the Recv is', Recv[0][1])
        stat_n = status_neighbour(Recv, rand_in[1], rank)
        stat_it = status_itself(stat_n, num_conn)
        comm.Barrier()
        set_flag(stat_it, rand_in)
        # print('It is process', rank, 'and the status is',
        #       stat_it[0], 'with data', rand_in)
        comm.Barrier()
        # -------------------figure 3.53------------------
        for i in range(it):
            fo = compare_in(Recv, rand_in, rank)
            # print('It is process', rank, 'and the max is', fo[0])
            comm.Barrier()
            randNum = copy.deepcopy(rand_in)
            randNum[1] = fo[0]
            send_msg(neigh, randNum, rank)
            # print('It is process', rank, 'and the Sent is', randNum[1])
            Recv = recv_msg(neigh, randNum, rank, data_receive)
            comm.Barrier()
        print('it is the process', rank, 'and the max is', fo[0])
