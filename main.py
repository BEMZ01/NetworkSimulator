import pygame, pygame.font, pygame.event, pygame.draw, string
from pygame.locals import *
import random


# Network simulator, using pygame to display the network and a GUI to connect nodes.
# Nodes are represented by circles, and connections are represented by lines.
# Nodes can be connected by clicking and dragging from one node to another.
# Nodes can be moved by clicking and dragging them.
# Nodes can be removed by right clicking them.
# Connections can be removed by right clicking them.


class Connection:
    def __init__(self, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b
        self.delay = 0
        self.ping()

    def ping(self):
        pygame.time.delay(self.delay)
        self.delay = random.randint(0, 0)

    def __str__(self):
        return f"--{self.node_a}-{self.delay}-{self.node_b}--"


class Node:
    def __init__(self, x, y, r, color, id):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.id = id

    def draw(self, screen):
        if CURRENT_VISIT == self.id:
            # outline with green if this node is the current node
            pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y), self.r, 2)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(str(self.id), True, (255, 255, 255))
        screen.blit(text, (self.x - 5, self.y - 5))

    def move(self, x, y):
        self.x = x
        self.y = y

    def is_clicked(self, x, y):
        return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.r ** 2

    def get_connections(self):
        global NETWORK
        connections = []
        for connection in NETWORK.connections:
            if connection.node_a == self:
                connections.append(connection)
            elif connection.node_b == self:
                connections.append(connection)
        return connections

    def process(self, message):
        command, data = message.split("=", 1)
        from_node, command = command.split(":")
        print(f"Received message {message} from {from_node}!")

    def send(self, message, destination, depth=10, visited=None):
        global CURRENT_VISIT
        # recursive function to send a message to a destination node.
        # the message will be passed through all the connections between the two nodes.
        # the message will be delayed by the delay of each connection.
        # the message will be printed out at each node.
        # if we are the destination node, print the message.
        if visited is None:
            visited = []
        elif destination.id in visited:
            # packet has already been sent successfully!
            return
        if depth == 0:
            print("Max depth reached")
            return
        print(f"Hello, I'm {self}. Received message {message}, destination: {destination}, visited: {visited}")
        CURRENT_VISIT = self.id
        visited.append(self.id)
        if self == destination:
            self.process(message)
            return
        connections = self.get_connections()
        connections.sort(key=lambda x: x.delay, reverse=True)
        for connection in connections:
            if connection.node_a == self:
                away_node = connection.node_b
            else:
                away_node = connection.node_a
            if away_node.id not in visited:
                if away_node == destination:

                    connection.ping()
                    away_node.send(message, destination, depth-1, visited)
                else:
                    # not directly connected to destination, so send to fastest node
                    pygame.time.delay(connection.delay)
                    connection.ping()
                    away_node.send(message, destination, depth-1, visited)
                    return
        # if we get here, this could be a dead end
        # if there are no more nodes to send to, send back to the previous node
        # first, get the return connection
        print(f"Dead end, returning to {visited[-2]}")
        return_connection = None
        for connection in connections:
            away_node = connection.node_b if connection.node_a == self else connection.node_a
            if away_node.id == visited[-2]:
                return_connection = connection
                break
        if return_connection is None:
            print("No return connection found")
            return
        # send the message back to the previous node, there should be a connection between the two
        return_connection.ping()
        away_node.send(message, destination, depth-1, visited)

    def __str__(self):
        return str(self.id)


class Network:
    def __init__(self):
        self.nodes = []
        self.connections = []

    def locate_node(self, x, y, radius):
        for node in self.nodes:
            if (x - node.x) ** 2 + (y - node.y) ** 2 <= radius ** 2:
                return node
        return None

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def draw(self, screen):
        for node in self.nodes:
            node.draw(screen)
        for connection in self.connections:
            node_a = connection.node_a
            node_b = connection.node_b
            pygame.draw.line(screen, CONNECTION_COLOR, (node_a.x, node_a.y), (node_b.x, node_b.y))
            # at the center of the line, display the delay
            font = pygame.font.SysFont("Arial", 20)
            text = font.render(str(connection.delay), True, CONNECTION_COLOR)
            screen.blit(text, ((node_a.x + node_b.x) // 2, (node_a.y + node_b.y) // 2))

    def get_node(self, x, y):
        for node in self.nodes:
            if node.is_clicked(x, y):
                return node
        return None

    def get_node_by_id(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        return None

    def get_connection(self, x, y):
        for connection in self.connections:
            node_a = connection.node_a
            node_b = connection.node_b
            if (x - node_a.x) ** 2 + (y - node_a.y) ** 2 <= node_a.r ** 2:
                return connection
            elif (x - node_b.x) ** 2 + (y - node_b.y) ** 2 <= node_b.r ** 2:
                return connection
        return None

    def create_connection(self, node1, node2):
        self.connections.append(Connection(node1, node2))


def get_node_colour():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            return event.key
        else:
            pass


def display_box(screen, message):
    "Print a message in a box in the middle of the screen"
    print(message)
    fontobject = pygame.font.Font(None, 18)
    pygame.draw.rect(screen, (0, 0, 0),
                     ((screen.get_width() / 2) - 100,
                      (screen.get_height() / 2) - 10,
                      200, 20), 0)
    pygame.draw.rect(screen, (255, 255, 255),
                     ((screen.get_width() / 2) - 102,
                      (screen.get_height() / 2) - 12,
                      204, 24), 1)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                    ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


def ask(screen, question):
    "ask(screen, question) -> answer"
    pygame.font.init()
    current_string = []
    display_box(screen, question + ": " + "".join(current_string))
    while running:
        inkey = get_key()
        if inkey == K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == K_ESCAPE:
            current_string = None
            break
        elif inkey == K_RETURN:
            break
        elif inkey == K_MINUS:
            current_string.append("_")
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_box(screen, question + ": " + "".join(current_string))
    return "".join(current_string) if current_string else False


if __name__ == '__main__':
    # init pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Network Simulator")
    clock = pygame.time.Clock()
    running = True
    drawing_connection = False
    mode = "move"
    NETWORK = Network()
    NODE_ID = 0
    CONNECTION_ID = 0
    NODE_RADIUS = 10
    NODE_COLOR = (255, 255, 255)
    CONNECTION_COLOR = (180, 180, 180)
    SELECTED_NODE = None
    SELECTED_CONNECTION = None
    CURRENT_VISIT = None
    while running:
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # handle mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                # left click
                if event.button == 1:
                    if mode == "connection":
                        mouse_pos = pygame.mouse.get_pos()
                        # find nearest node within range
                        node = NETWORK.locate_node(mouse_pos[0], mouse_pos[1], NODE_RADIUS)
                        if SELECTED_NODE is not None and node is not None:
                            NETWORK.create_connection(SELECTED_NODE, node)
                            SELECTED_NODE = None
                            drawing_connection = False
                        else:
                            SELECTED_NODE = node
                            drawing_connection = True
                    elif mode == "move":
                        # if a node is clicked, select it
                        mouse_pos = pygame.mouse.get_pos()
                        node = NETWORK.get_node(mouse_pos[0], mouse_pos[1])
                        if node is not None:
                            SELECTED_NODE = node
                        else:
                            SELECTED_NODE = None
                        # if a connection is clicked, select it
                        connection = NETWORK.get_connection(mouse_pos[0], mouse_pos[1])
                        if connection is not None:
                            SELECTED_CONNECTION = connection
                        else:
                            SELECTED_CONNECTION = None
                # right click
                elif event.button == 3:
                    # remove node
                    if SELECTED_NODE is not None:
                        SELECTED_NODE.remove()
                        NETWORK.remove_node(SELECTED_NODE)
                        SELECTED_NODE = None
                    # remove connection
                    if SELECTED_CONNECTION is not None:
                        SELECTED_CONNECTION.remove_connection(SELECTED_CONNECTION)
                        SELECTED_CONNECTION = None
            if event.type == pygame.MOUSEBUTTONUP:
                # left click
                if event.button == 1:
                    # deselect node
                    if SELECTED_NODE is not None and mode == "move":
                        SELECTED_NODE = None
                    # deselect connection
                    if SELECTED_CONNECTION is not None and mode == "move":
                        SELECTED_CONNECTION = None

            # handle mouse motion
            if event.type == pygame.MOUSEMOTION:
                # move node
                if SELECTED_NODE is not None and mode == "move":
                    SELECTED_NODE.move(event.pos[0], event.pos[1])
            # handle key events
            if event.type == pygame.KEYDOWN:
                # add node
                if event.key == pygame.K_n:
                    mouse_pos = pygame.mouse.get_pos()
                    NETWORK.add_node(Node(mouse_pos[0], mouse_pos[1], NODE_RADIUS, get_node_colour(), NODE_ID))
                    NODE_ID += 1
                # add connection
                if event.key == pygame.K_c:
                    if drawing_connection:
                        mode = "connection"
                    else:
                        mode = "move"
                    drawing_connection = not drawing_connection

                if event.key == pygame.K_p:
                    # ping between two nodes
                    while True:
                        node1 = int(ask(screen, "Node 1 ID"))
                        node2 = int(ask(screen, "Node 2 ID"))
                        if node1 is False or node2 is False:
                            break
                        # check if node1 and node2 are valid
                        node1 = NETWORK.get_node_by_id(node1)
                        node2 = NETWORK.get_node_by_id(node2)
                        if node1 is not None and node2 is not None:
                            break
                        else:
                            print("Invalid node IDs")
                    if node1 is not False and node2 is not False:
                        node1.send(f"{node1.id}:PING=", node2)
        screen.fill((0, 0, 0))
        NETWORK.draw(screen)
        if drawing_connection and SELECTED_NODE is not None:
            pygame.draw.line(screen, CONNECTION_COLOR, (SELECTED_NODE.x, SELECTED_NODE.y), pygame.mouse.get_pos())
        # display the current mode at the top left corner
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(f"Mode: {mode}", True, (255, 255, 255))
        screen.blit(text, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
