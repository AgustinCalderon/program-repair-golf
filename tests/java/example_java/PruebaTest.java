import static org.junit.Assert.*;

import org.junit.Test;

public class PruebaTest {

    @Test
    public void test1() {
        int a = 1;
        int b = 2;
	    int result = Prueba.prueba(a, b);
	    assertEquals(0, result);
    }
    
    @Test
    public void test2() {
        int a = 2;
        int b = 1;
        int result = Prueba.prueba(a, b);
        assertEquals(1, result);
    }

    @Test
    public void test3() {
        int a = 1;
        int b = 1;
        int result = Prueba.prueba(a, b);
        assertEquals(2, result);
    }

}
