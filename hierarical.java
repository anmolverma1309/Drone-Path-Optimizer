
class Animal {
    void eat() {
        System.out.println("This animal is eating food.");
    }
}

class Dog extends Animal {
    void bark() {
        System.out.println("The dog says: Woof Woof!");
    }
}

class Cat extends Animal {
    void meow() {
        System.out.println("The cat says: Meow Meow!");
    }
}

public class hierarical {
    public static void main(String[] args) {

        Dog myDog = new Dog();
        myDog.eat();
        myDog.bark();

        System.out.println("---");

        Cat myCat = new Cat();
        myCat.eat();
        myCat.meow();
    }
}