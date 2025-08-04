import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));


        int N = Integer.parseInt(br.readLine());

        StringTokenizer st = new StringTokenizer(br.readLine());

        int minNum = 1000000;

        int maxNum = 2;

        for (int i = 0 ; i < N ; i++) {
            int A = Integer.parseInt(st.nextToken());
            if (A < minNum) {
                minNum = A;
            } 
            if (A > maxNum) {
                maxNum = A;
            }
        }

        System.out.println(minNum * maxNum);
    }
}