












IMPLEMENTATION REPORT FOR FEDERAL AVIATION ADMINISTRATION
FLIGHTGUI APPLICATION


Spring 2008, Phase 3 Collaborative Effort Between:
Fairfield University, MS Software Engineering Program Students and Rowan University, Computer Science Students



Prepared by:
for Fairfield University:
Rebecca Docimo Neha Mathur Rachna Parmar

for Rowan University: Hristo Asenov Andrew Fabian Eric Thomas
 

Table of Contents- FlightGUI Implementation Report

Implementation Language	…………………………………	Page 3
Coding Conventions	…………………………………	Page 3
Purpose	…………………………………	Page 3
File Names	…………………………………	Page 3
File Header	…………………………………	Page 4
Comments	…………………………………	Page 5
Variable Names	…………………………………	Page 7
Method Arguments	…………………………………	Page 7
Parentheses, braces and indentation	…………………………………	Page 8
Control Structures	…………………………………	Page 10
 

Implementation Language
The FlightGUI team chose the Java language to implement FlightGUI. In addition, Java OpenGL (JOGL) is being used. OpenGL is the open source implementation of a graphics library in order to add enhanced graphics capabilities to an application, such as the ability to render 3D shapes. JOGL is designed to provide hardware-supported 3D graphics to applications written specifically in Java. The database, also customer driven, is Oracle.
Oracle is an extremely robust RDBMS that is well suited to the data-intensive needs of the FAA and provides excellent audit and recovery tools.
While the use of Java was customer-driven, there are many good reasons to use Java for this project. First, Java is non-proprietary. The development kits are free and easy to get. The runtime platform is also free and easy to get and is now almost universally available on all machines since Java is so widely used. For example, Sun estimated at the 2006 JavaOne conference that there are over one billion java-enabled phones and pdas. Many programmers today also know Java so it is easy to staff a project. Java is also theoretically platform independent so that it would likely be a lot easier to manage than other languages if the platform to run the application on was later changed.
The easy integration of Java with JOGL also makes Java a clear choice. This functionality is required in order to draw enhanced 2D and 3D shapes on which the application relies. Java also allows for complex GUIs to be drawn which is a key feature of this application. Java is also very flexible so that if the project needs change, the application can later be redeployed as a web application from a desktop application without having to start from scratch. It also has features such as Java Web Start, something the project uses now, which allows the application and new features to be easily released to users.


Coding Conventions for FlightGUI Application

Purpose
To give a description of the coding standards that are used in the application.

File Names
HTML documents use the suffix .html Java source files use the suffix .java Compiled java files use the suffix .class
Java archives (application bundle for easy deployment) use the suffix .jar

Example: FlightData.java, FlightGUI.jar
 


File Header
Each source file will begin with a header as shown below which states the file name, the author(s), the purpose of the file and the current CVS version of the file. The order of information at the top of the file will be:

1.	Package statement
2.	Import statements
3.	Version data enclosed in a multi-line regular comment
4.	File header comment in javadoc format explaining file purpose, authors, etc.

Javadoc is used for the header based on a requirement of the customer. Javadoc comments enable programmers to embed program documentation directly in their programs. This is the industry-standard method of in-program documentation for Java. Javadoc is included with the JDK and more information can be found at: http://java.sun.com/javase/6/docs/technotes/guides/javadoc/index.html

The standard format for javadoc comments will be used which is to start with /** and end with */. All lines within the end delimiters will begin with a single asterisk “*”.

/**
*	File name: FlightClass.java
*	Purpose: Is to create a class for flights.
*	
*	@author Name1 and Name2
*	@version $Revision: 1.1 $
*/

In addition, versioning information will be included within standard multi-line comment notation (see below for more on this). The version noted in the javadoc header will be the latest version (i.e. the highest version number).
/*
*	$Log: ArtccSpace.java,v $
*	Revision 1.1 2007/06/07 13:37:31 confesors
*	Initial import
*	
*	
*/
 


Comments
There are various comment types within the source code.

First, we have javadoc comments. This includes the header and comments within the class bodies. Examples of these are shown, respectively, below. The comments within the class bodies are in javadoc format so that they may be part of the documentation that can be parsed and viewed in a single standardized format. There are typically one per method and one per variable and preceed the method or variable.

Next we have non-javadoc multi-line comments. These are anything that will not be included in the javadoc and are multi-line. An example is the versioning information as shown below. Anything else we do not want to appear in javadoc can use this syntax.

Finally, we have single line, non-javadoc comments. These are anything that should not appear in javadoc and are on a single line. This includes end of line comments.
Typically single-line, non-javadoc comments are used as markers that should not print in the javadoc because they would not make sense apart from their code fragment. One such example is if we want to note the end of a loop at the end of its closing bracket just to enhance readability like “} // end of inner for loop”. We might also alert other programmers to something using single-line comments, such as to say that a function should be looked at again. These type of comments can be used on its own line like:
// here is a whole line comment or, at the end of a line of code:
int flightNum; // variable to accumulate number of flights taken

We can also use single-line, non-javadoc comments to comment out debug statements (such as print-line statements to check that our values are correct) that may be used again. Finally, single-line comments could be used if we remove a piece of functionality by commenting it, but want to show it for reference or if we think the functionality might be added back later. These should be kept to a minimum, although they sometimes show important insights into the historical development of the code.

Header Javadoc Comment:
/**
*	File name: FlightClass.java
*	Purpose: Is to create a class for flights.
*	
*	@author Name1 and Name2
*	@version $Revision: 1.1 $
 

*/

Javadoc Comment within a Class file:
/**
*	A container to hold the name of the ArtccSpace
*/
private String artcc_name;

Non-Javadoc Multi-line Comment
/*
*	$Log: ArtccSpace.java,v $
*	Revision 1.1 2007/06/07 13:37:31 confesors
*	Initial import
*	
*	
*/

Single-line Non-Javadoc Comment

Example 1- in-code marker:
if (pad == 4)  // <==== Bug correction

Example 2- in-code marker:
public class BMPFile extends Component {
//--- Private constants
private final static int BITMAPFILEHEADER_SIZE = 14; private final static int BITMAPINFOHEADER_SIZE = 40;

Example 3- removing functionality, but leaving it for reference or because it may be used again:
protected boolean isElvis() { boolean retBool = false; try {
//makeConnection();
if ((conn.getMetaData().getURL().indexOf("elvis")) > 0) { retBool = true;
}
//conn.close();
}
 

Example 4- checker or debug statements that we may want to use again:
DatabaseQuery query = new DatabaseQuery(); CachedRowSetImpl result;
result = query.getArtccInfo(artcc_name);
//	System.out.println("SIZE: " + result.size());


Variable Names
Names of various program parts for the most part follow the Java standards.
The only case where Java standards may not be followed is for member or method names that are part of a code fragment written by another source and incorporated into our code. This is to avoid changing code that has already been created and causing unknown effects by doing so.

Identifier	Convention	Examples
class names	capitalize each word in name	public class Flight { public class FlightData {
methods	lowercase first word, capitalize all other words	drawSector(); stop();
class member names	lowercase first word, capitalize all other words OR lowercase all words with underscores in between them.
NOTE: the majority of variables follow the Java standard (the first two examples). The variables with an underscore are typically within code that was taken from a third party source. All new variables follow the
Java standard.	int numberFlights; String sid;
String jdbc_parameter;
named constants	all caps, use underscores to separate words- these are very common when using GUIs	final color GREEN; Color.RED; JFrame.EXIT_ON_CLOSE;
Method Arguments
When we call a method we have declared somewhere, we will provide arguments so that the method can carry out its task. The arguments will just be names and will not include any data types.
 

If the method we are calling specifies a String parameter we will enclose the argument in double quotes. If it is of type int, double or float we will not use double quotes. If it is a boolean we can also specify true or false without double quotes.

We will specify arguments in the same order as the method parameters were specified. Each argument will be separated by a comma. An argument list may include arguments of different types, such as some being Strings and some being numerical types. The types of the arguments must match the types that were specified in the method declaration parameter list. If a parameter is declared as a String, our argument in the same place in the list must also be a String.
An argument can be a call to another method which will obtain the value for passing to the method we are calling.

Example- method call as arg1, string as arg2:
Registrar.register(this.getClass().getName(), "$Revision: 1.8 $");

Example- string as both arg1 and arg2:
defaultProperties.put("applyDistort", "false");

Example- boolean as arg1:
addAConflictMenuItem.setEnabled(false);

Parentheses, braces and indentation
Parentheses will be of the format:
void updateWindow(int index) { for(int i = 0; i < tabs.size(); i++)
tabs.get(i).updateWindow(index);
}

Braces will be of the format, with the opening brace coming immediately after the class or method name and 1 space, and the closing brace being on it’s own line at the end:

public class FlightData {

… class body
}

Identations:
The class declaration will be farthest out (no indentation) along with import and package statements.
 

Then, each lower level within the class body will be indented one tab by clicking the tab key on the keyboard.

Each method and global variable will be indented 1 tab from the class declaration.

The statements within each method will be indented 1 tab from the method declaration.

The first control structure within a method will be indented 1 tab from the method declaration. Statements inside the control structure will be indented 1 tab from the control structure declaration. Any nested control structures will be indented 1 tab from the declaration of the previous control structure’s declaration.

Example:
/**
*	File Name: About.java
*
*	@author Joe Smith
*	
*	Purpose: The purpose of this class is to display the
*	about window to the user.
*/
package gov.faa.cpat.FlightGUI; import java.util.*;
import javax.swing.*;

public class About extends javax.swing.JFrame {

/**
* Creates a singleton instance of the About class
*/
public static About singletonAbout;

/**
* Creates new form About and sets it to be placed in the middle of the screen.
*/
private About() {
Registrar.register(this.getClass().getName(), "$Revision: 1.5 $"); initComponents();
screenSize = Toolkit.getDefaultToolkit().getScreenSize(); this.setLocation((screenSize.width/2)-215, (screenSize.height/2)-106);
}

/**
 

* Nullifies the About window object.
*/
public void makeNull(){ singletonAbout = null;
}
}

Control Structures

For loops

Multiple statements
for(int i = 0; i < tabs.size(); i++){ statement1;
statement2;
}

or Single Statement

for(int i = 0; i < tabs.size(); i++)
tabs.get(i).updateWindow(index);

If Statements
if (condition) {
statements;
 
}
else {

}
 

statements;
 

While Loops
while (width <= 0 || height <= 0){ width = textureFile.getWidth(null); height = textureFile.getHeight(null);
}

Switch Statements
switch(errorCode) { case 13:
shiftX = -1;
shiftY = 1; break;
 

case 14:
shiftX = 1;
shiftY = 1; break;
case 7:
shiftX = 1;
shiftY = -1; break;
default:
shiftX = 0;
shiftY = 0;
}
