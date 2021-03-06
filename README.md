# Max_election_MPI

  The Python-based message passing interface (MPI) implementation of a leader election algorithm is presented. Each node generate a 64-bit random integer number initially. Using MPI protocol, they aim to reach a consensus what the maximum value among them is. For implementation purpose, “mpi4py” library is used for parallel programming/computing to emulate distributed machines (nodes) with message passing protocol. Two different algorithms are implemented, each with its own pros and cons.
	 In the first implementation (associated to file “practice_mpi.py") a ring topology (sometimes called loop network) is implemented. A ring consists of a single cycle of length “n” where “n” is the number of nodes . In a ring topology, each entity/node has exactly two neighbours. In this leader election implementation, each node transmits a message consisting of the ID and the generated random number to it right side neighbour (clockwise in ring) only if the received message from its left side neighbour is larger than the generated random number. 
Each node will eventually see the ID of everybody else (finite communication delays) including the maximum value. Based on this, the largest number among nodes get this opportunity to flow through whole network for consistent agreement on largest value. In the case that, the node receive a message with the same ID it has (the ID of the received node is containing in the message header), it announced that it is the leader and the message circulation should stop. Upon receiving leader announcement message, all nodes stop transmitting and announce the largest value they agree on. 
	In second leader election implementation (associated to file “k_reg_iter.py"), the nodes are connected through k-regular graph where the degree of each node is the same. In the case that the k-regualr node cannot be constructed, an error will be thrown. In this algorithm, after each node generate 64-bit random number, it exchanges its value and ID with its neighbours to determine its status. The status of the node can be labeled as sink, internal or source. Using this, we constructed a directed graph where each edge in graph is directed toward the node with higher value. In the resulted connected graph, a sink node (with all inward neighbours) contains the lowest value among its neighbours and source node (with all outward neighbours) contain highest value among it neighbours. After initialisation phase, each node compares the values received from inward neighbours and send the maximum value to the outward neighbours. Using this, the amount of message passing is minimised as each node sends only to the outward nodes. Based on this, the message of sources get this opportunity to flow through whole network (from source nodes to sink nodes). 

Pros and Cons:
  The pros of ring topology is that, the nodes know when to terminate the agreement as there is an explicit announcement message after leader determination. However, the topology requires that the number of connected neighbours is limited to two. In the second, more general topology is supposed as each node is connected to exactly "n/10" nodes where “n” is total number of nodes. However, there is no explicit termination message for announcement such as the one exists in ring topology. We can improve the algorithm by using universal leader election such as Mega-Merger and YO-YO algorithms which is left for future.
  
  
  Running the program:
  
  For running the prgram type in terminal for linux:
  mpirun -n number_of_node python3 file_name.py
  
  For example for running the "k_reg_iter.py" with 30 nodes we will type:
  mpirun -n 30 python3 k_reg_iter.py
  
