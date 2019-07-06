# Basic 3D Renderer implementation
import pygame, math, sys, os

# Functions
def rotate2d(pos, rad):
    xPos, yPos = pos;
    sin, cos = math.sin(rad), math.cos(rad);
    return xPos * cos - yPos * sin, yPos * cos + xPos * sin

def lockMouse():
    pygame.event.get(); pygame.mouse.get_rel() # Get relative position of the mouse
    pygame.mouse.set_visible(0); pygame.event.set_grab(1) # Hide the mouse and lock to screen

# Classes
class Camera:
    # Initialise the camera to a base position & rotation
    def __init__(self, pos=(0,0,0), rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)

    # Manage mouse events
    def events(self, event):
        if event.type == pygame.MOUSEMOTION:
            xPos, yPos = event.rel
            self.rot[0] += yPos/200
            self.rot[1] += xPos/200
    
    # Update the Camera to reflect keyboard input
    def update(self, deltaTime, keyPress):
        speed = deltaTime * 10 # Create speed constant using delta time 

        if keyPress[pygame.K_q]: self.pos[1] -=speed # Move up 
        if keyPress[pygame.K_e]: self.pos[1] +=speed # Move Down
        # Account for mouse rotation
        xPos, yPos = speed * math.sin(self.rot[1]), speed * math.cos(self.rot[1]) 
        if keyPress[pygame.K_w]: self.pos[0] += xPos; self.pos[2] += yPos # Move Forward
        if keyPress[pygame.K_s]: self.pos[0] -= xPos; self.pos[2] -= yPos # Move Backward
        if keyPress[pygame.K_a]: self.pos[0] -= yPos; self.pos[0] += xPos # Move Left
        if keyPress[pygame.K_d]: self.pos[0] += yPos; self.pos[2] -= xPos # Move Right

class Cube:
    # Vertices points in screen space
    vertices = (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1), (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)

    # Faces
    faces = (0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (0,3,7,4), (1,2,6,5)
    faceColours = (0,0,255), (255,0,0), (255,255,255), (255,255,0), (0,255,0), (255,127,0)

    # Initialise default cube position in screen space & vertices positions 
    def __init__(self, pos = (0,0,0)):
        xPos, yPos, zPos = pos
        self.verts = [(xPos+x/2, yPos+y/2, zPos+z/2) for x, y, z in self.vertices]

def main():
    pygame.init() # Initialize pygame modules
    width,height = 500,500; # Window size constants
    cx,cy = width//2,height//2
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    window = pygame.display.set_mode((width,height))
    pygame.display.set_caption("3D Rendering in Python")
    timer = pygame.time.Clock()
    cam = Camera((0,0,-5)) # Spawn the camera slightly stepped back from the oject space

    lockMouse()
    
    # Define cube positions
    cubes = (Cube((0,0,0)), Cube((-2,0,0)), Cube((2,0,0)), Cube((0,-2,0)), Cube((-2,-2,0)), Cube((2,-2,0)), Cube((0,2,0)), Cube((-2,2,0)), Cube((2,2,0)),
    Cube((0,0,-2)), Cube((-2,0,-2)), Cube((2,0,-2)),
    Cube((0,-2,-2)), Cube((-2,-2,-2)), Cube((2,-2,-2)),
    Cube((0,2,-2)), Cube((-2,2,-2)), Cube((2,2,-2)),
    Cube((0,0,2)), Cube((-2,0,2)), Cube((2,0,2)),
    Cube((0,-2,2)), Cube((-2,-2,2)), Cube((2,-2,2)),
    Cube((0,2,2)), Cube((-2,2,2)), Cube((2,2,2)))

    # Start the Game Loop
    while True:
        deltaTime = timer.tick()/1000
        # Input & Camera updates
        keyPress = pygame.key.get_pressed()
        cam.update(deltaTime,keyPress)

        # Set window close / escape key / alt f4 exit points
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                elif event.key == pygame.K_F4 and keyPress[pygame.K_LALT]: pygame.quit(); sys.exit()
            cam.events(event)

        # Fill background grey
        window.fill((30,80,100)) 

        # Create data arrays for polygons & depth info 
        face_array = []
        face_colour = []
        depth = []
        
        # Loop through all objects to find faces to render
        for obj in cubes:
            vert_array = []; screen_coords = []
            for xPos, yPos, zPos in obj.verts:   
                # Set position to update == camera position
                xPos -= cam.pos[0]
                yPos -= cam.pos[1]
                zPos -= cam.pos[2]
                xPos, zPos = rotate2d((xPos,zPos), cam.rot[1])
                yPos, zPos = rotate2d((yPos,zPos), cam.rot[0])
                
                vert_array += [(xPos, yPos, zPos)]

                # Set feild of view
                fov = 250/zPos
                xPos,yPos = xPos*fov, yPos*fov
                screen_coords += [ (cx+int(xPos), cy+int(yPos)) ]

            # Loop through the current cubes faces    
            for f in range(len(obj.faces)):
                face = obj.faces[f]
                visible = False 

                # If a face is on screen then set visible to True
                for i in face:
                    xPos, yPos = screen_coords[i]
                    if vert_array[i][2] > 0 and xPos > 0 and xPos < width and yPos > 0 and yPos < height : visible = True; break

                # When a face comes on screen, it needs to be added to the data arrays & it's depth needs to be calculated
                if visible:
                    coords = [screen_coords[i] for i in face]
                    face_array += [coords]
                    face_colour += [obj.faceColours[f]]
                    depth += [sum (sum(vert_array[j][i]/len(face) for j in face)**2 for i in range(3))]

        # Final drawing pass, calculating correct draw order based on the face depth
        drawOrder = sorted(range (len(face_array)), key = lambda i: depth[i], reverse = 1)

        for i in drawOrder:
            try: pygame.draw.polygon(window, face_colour[i], face_array[i])
            except: pass
            
        pygame.display.flip()

if __name__ == '__main__':
    main()
