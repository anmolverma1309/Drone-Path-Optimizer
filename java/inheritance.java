class animal{
    void bark(){
        System.out.println("dog barks");
    }
}
class dog extends animal{
    void eat(){
        System.out.println("dog eats grass");
    }
};

public class inheritance{
    public static void main(String[] args) {
        dog d = new dog();
        d.eat();
        d.bark();
    }
}