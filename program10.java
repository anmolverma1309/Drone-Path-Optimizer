// First Interface
interface Printable {
    void print();
}

// Second Interface
interface Showable {
    void show();
}

// A single class implementing multiple interfaces
class Document implements Printable, Showable {

    @Override
    public void print() {
        System.out.println("Printing the document...");
    }

    @Override
    public void show() {
        System.out.println("Displaying the document on screen...");
    }
}

public class program10 {
    public static void main(String[] args) {
        Document myDoc = new Document();

        // Demonstrating that the class has inherited
        // capabilities from both interfaces
        myDoc.print();
        myDoc.show();
    }
}