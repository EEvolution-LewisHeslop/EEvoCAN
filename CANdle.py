from HwManager import HwManager
import canopen
import time

class CANdle:
    def __init__(self, hwManager:HwManager):
        self.hwManager = hwManager

    def search_for_nodes(self, network=None):
        firstNetwork = self.hwManager.activeCanopenNetworks[0]
        if (network is None):
            network:canopen.Network = firstNetwork[0]
        network.scanner.search()
        # We may need to wait a short while here to allow all nodes to respond
        time.sleep(0.05)
        for node_id in network.scanner.nodes:
            print("Found node %d!" % node_id)
            network.add_node(node_id)

    # Sdo write based on the use of SdoServer
    def sdo_write(self, nodeId, index, subindex, data, network=None):
        # Check if there is at least one active CANopen network
        if (network == None and not self.hwManager.activeCanopenNetworks):
            return "Error: No available canopen networks for sdo_write."

        # Access the first CANopen network
        firstNetwork = self.hwManager.activeCanopenNetworks[0]

        if (network is None):
            network:canopen.Network = firstNetwork[0]

        # Access the node from the network
        node = network.nodes[nodeId]

        # Send the SDO
        try:
            # Write
            node.sdo.download(index, subindex, data)
            print("SDO write operation successful.")
            return "OK"
        except Exception as e:
            print(f"Error in SDO operation: {e}")
            return f"Error in SDO operation: {e}"

    # Sdo write based on the use of SdoVariable
    def sdo_wnx(self, nodeId, index, subindex, data, network=None):
        """
        Write data to an SDO on a CANopen network.

        :param nodeId: The node ID on the CANopen network.
        :param index: The index of the object to write to.
        :param subindex: The subindex of the object to write to.
        :param data: The data to write.
        :param network: The CANopen network object.
        :return: 'OK' on success, or an Error message on failure.
        """
        try:
            # Check if there is at least one active CANopen network
            if (network == None and not self.hwManager.activeCanopenNetworks):
                return "Error: No available canopen networks for sdo_wnx."

            # Access the first CANopen network
            firstNetwork = self.hwManager.activeCanopenNetworks[0]

            if (network is None):
                network = firstNetwork

            # Access the node
            node = network[nodeId]

            # Write data to the SDO
            node.sdo[index][subindex].raw = data

            return "OK"
        except canopen.SdoCommunicationError as e:
            return f"SDO communication Error: {e}"
        except canopen.SdoAbortedError as e:
            return f"SDO abort Error: {e}"
        except KeyError:
            return "Error: Node ID not found on network"
        except Exception as e:
            return f"Unexpected Error: {e}"
        
    # Sdo read based on the use of SdoServer
    def sdo_read(self, nodeId, index, subindex, network=None):
        # Check if there is at least one active CANopen network
        if (network == None and not self.hwManager.activeCanopenNetworks):
            return "Error: No available canopen networks for sdo_read."

        # Access the first CANopen network
        firstNetwork = self.hwManager.activeCanopenNetworks[0]

        if (network is None):
            network = firstNetwork

        # Access the node from the network
        node = network[nodeId]

        # Send the SDO
        try:
            # Read
            data = node.sdo.upload(index, subindex)
            print("SDO read operation successful.")
            return data
        except Exception as e:
            return f"Error in SDO operation: {e}"
        
    # Sdo read based on the use of SdoVariable
    def sdo_rnx(self, nodeId, index, subindex, network):
        """
        Read data from an SDO on a CANopen network.

        :param nodeId: The node ID on the CANopen network.
        :param index: The index of the object to read from.
        :param subindex: The subindex of the object to read from.
        :param network: The CANopen network object.
        :return: The read data on success, or an Error message on failure.
        """
        try:
            # Check if there is at least one active CANopen network
            if (network == None and not self.hwManager.activeCanopenNetworks):
                return "Error: No available canopen networks for sdo_write."

            # Access the first CANopen network
            firstNetwork = self.hwManager.activeCanopenNetworks[0]

            if (network is None):
                network = firstNetwork

            # Access the node from the network
            node = network[nodeId]

            # Read data from the SDO
            data = node.sdo[index][subindex].raw
            return data
        except canopen.SdoCommunicationError as e:
            return f"SDO communication Error: {e}"
        except canopen.SdoAbortedError as e:
            return f"SDO abort Error: {e}"
        except KeyError:
            return "Error: Node ID not found on network"
        except Exception as e:
            return f"Unexpected Error: {e}"