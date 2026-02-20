class Person {
    String name;
    int age;

    void setPersonDetails(String name, int age) {
        this.name = name;
        this.age = age;
    }

    void displayPerson() {
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);
    }
}

class Student extends Person {
    int studentId;

    void setStudentDetails(int id) {
        this.studentId = id;
    }

    void displayStudentInfo() {
        displayPerson();
        System.out.println("Student ID: " + studentId);
    }
}

public class program8 {
    public static void main(String[] args) {

        Student s1 = new Student();

        s1.setPersonDetails("Anmol Verma", 18);
        s1.setStudentDetails(1001);

        System.out.println("--- Student Details ---");
        s1.displayStudentInfo();
    }
}